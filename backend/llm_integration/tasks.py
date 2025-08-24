import logging
from typing import Dict, List, Any
from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from .models import LLMModel, LLMProcessingConfig
from .services import LLMService
from documents.models import Document
from entities.models import Entity, EntityType
from processing.models import ProcessingJob

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def extract_entities_from_text(
    self, text: str, document_id: int, prompt_type: str = "marsiya", user_id: int = None
):
    """
    Extract entities from text using LLM in the background.

    Args:
        text: The text to process
        document_id: ID of the document being processed
        prompt_type: Type of prompt to use (general, urdu, marsiya, custom)
        user_id: ID of the user requesting the processing
    """
    try:
        # Get the document
        document = Document.objects.get(id=document_id)

        # Create or update processing job
        job, created = ProcessingJob.objects.get_or_create(
            document=document,
            job_type="entity_extraction",
            defaults={
                "status": "processing",
                "progress": 0,
                "created_by_id": user_id,
                "metadata": {
                    "prompt_type": prompt_type,
                    "text_length": len(text),
                    "llm_model": "pending",
                },
            },
        )

        if not created:
            job.status = "processing"
            job.progress = 0
            job.started_at = timezone.now()
            job.metadata.update(
                {
                    "prompt_type": prompt_type,
                    "text_length": len(text),
                    "llm_model": "pending",
                }
            )
            job.save()

        # Update progress
        job.progress = 10
        job.save()

        # Initialize LLM service
        try:
            llm_service = LLMService()
            job.metadata["llm_model"] = llm_service.llm_model.model_name
            job.save()
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            job.status = "failed"
            job.error_message = f"LLM service initialization failed: {str(e)}"
            job.completed_at = timezone.now()
            job.save()
            raise

        # Update progress
        job.progress = 20
        job.save()

        # Extract entities
        try:
            entities_data = llm_service.extract_entities(text, prompt_type)
            job.progress = 80
            job.save()
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            job.status = "failed"
            job.error_message = f"Entity extraction failed: {str(e)}"
            job.completed_at = timezone.now()
            job.save()
            raise

        # Save entities to database
        try:
            saved_entities = []
            for entity_data in entities_data:
                # Get entity type
                entity_type, _ = EntityType.objects.get_or_create(
                    name=entity_data["entity_type"].upper()
                )

                # Create entity
                entity = Entity.objects.create(
                    document=document,
                    text=entity_data["text"],
                    entity_type=entity_type,
                    start_position=entity_data["start"],
                    end_position=entity_data["end"],
                    confidence=entity_data.get("confidence", 0.8),
                    source="llm",
                    metadata={
                        "llm_model": entity_data.get("llm_model", "unknown"),
                        "prompt_type": entity_data.get("prompt_type", prompt_type),
                        "processing_time": entity_data.get("processing_time", 0),
                        "extraction_method": "llm",
                    },
                )
                saved_entities.append(entity)

            job.progress = 90
            job.save()

            # Update document metadata
            document.metadata.update(
                {
                    "last_processed": timezone.now().isoformat(),
                    "entities_count": len(saved_entities),
                    "processing_status": "completed",
                    "llm_model_used": llm_service.llm_model.model_name,
                    "prompt_type_used": prompt_type,
                }
            )
            document.save()

            # Update processing job
            job.status = "completed"
            job.progress = 100
            job.completed_at = timezone.now()
            job.result = {
                "entities_extracted": len(saved_entities),
                "entities_data": [
                    {
                        "id": entity.id,
                        "text": entity.text,
                        "entity_type": entity.entity_type.name,
                        "start": entity.start_position,
                        "end": entity.end_position,
                        "confidence": entity.confidence,
                    }
                    for entity in saved_entities
                ],
            }
            job.save()

            logger.info(
                f"Successfully extracted {len(saved_entities)} entities from document {document_id}"
            )

        except Exception as e:
            logger.error(f"Failed to save entities: {e}")
            job.status = "failed"
            job.error_message = f"Failed to save entities: {str(e)}"
            job.completed_at = timezone.now()
            job.save()
            raise

    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")
        raise
    except Exception as e:
        logger.error(f"Task failed: {e}")
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = timezone.now()
        job.save()

        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying task (attempt {self.request.retries + 1})")
            raise self.retry(exc=e)
        else:
            logger.error(f"Task failed after {self.max_retries} retries")
            raise


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def test_llm_connection(self, llm_model_id: int):
    """
    Test connection to an LLM provider.

    Args:
        llm_model_id: ID of the LLM model to test
    """
    try:
        llm_model = LLMModel.objects.get(id=llm_model_id)

        # Create processing job for tracking
        job, created = ProcessingJob.objects.get_or_create(
            job_type="llm_connection_test",
            metadata={"llm_model_id": llm_model_id},
            defaults={
                "status": "processing",
                "progress": 0,
                "metadata": {
                    "llm_model_id": llm_model_id,
                    "provider": llm_model.provider,
                    "model_name": llm_model.model_name,
                },
            },
        )

        if not created:
            job.status = "processing"
            job.progress = 0
            job.started_at = timezone.now()
            job.save()

        # Test connection
        try:
            llm_service = LLMService(llm_model)
            result = llm_service.test_connection()

            job.progress = 100
            job.status = "completed"
            job.completed_at = timezone.now()
            job.result = result
            job.save()

            # Update LLM model stats
            if result["success"]:
                llm_model.last_connection_test = timezone.now()
                llm_model.connection_status = "success"
                llm_model.save(
                    update_fields=["last_connection_test", "connection_status"]
                )
            else:
                llm_model.last_connection_test = timezone.now()
                llm_model.connection_status = "failed"
                llm_model.save(
                    update_fields=["last_connection_test", "connection_status"]
                )

            logger.info(
                f"LLM connection test completed for {llm_model.model_name}: {result['success']}"
            )
            return result

        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = timezone.now()
            job.save()

            # Update LLM model stats
            llm_model.last_connection_test = timezone.now()
            llm_model.connection_status = "failed"
            llm_model.save(update_fields=["last_connection_test", "connection_status"])

            raise

    except LLMModel.DoesNotExist:
        logger.error(f"LLM model {llm_model_id} not found")
        raise
    except Exception as e:
        logger.error(f"LLM connection test task failed: {e}")

        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(
                f"Retrying LLM connection test (attempt {self.request.retries + 1})"
            )
            raise self.retry(exc=e)
        else:
            logger.error(f"LLM connection test failed after {self.max_retries} retries")
            raise


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def bulk_entity_extraction(
    self, document_ids: List[int], prompt_type: str = "marsiya", user_id: int = None
):
    """
    Process multiple documents for entity extraction.

    Args:
        document_ids: List of document IDs to process
        prompt_type: Type of prompt to use
        user_id: ID of the user requesting the processing
    """
    try:
        total_documents = len(document_ids)
        processed_count = 0
        failed_count = 0

        # Create bulk processing job
        job, created = ProcessingJob.objects.get_or_create(
            job_type="bulk_entity_extraction",
            metadata={"document_count": total_documents},
            defaults={
                "status": "processing",
                "progress": 0,
                "created_by_id": user_id,
                "metadata": {
                    "document_count": total_documents,
                    "prompt_type": prompt_type,
                    "processed": 0,
                    "failed": 0,
                },
            },
        )

        if not created:
            job.status = "processing"
            job.progress = 0
            job.started_at = timezone.now()
            job.metadata.update(
                {
                    "document_count": total_documents,
                    "prompt_type": prompt_type,
                    "processed": 0,
                    "failed": 0,
                }
            )
            job.save()

        for i, doc_id in enumerate(document_ids):
            try:
                # Update progress
                progress = int((i / total_documents) * 100)
                job.progress = progress
                job.save()

                # Process individual document
                extract_entities_from_text.delay(
                    text="",  # Will be fetched from document
                    document_id=doc_id,
                    prompt_type=prompt_type,
                    user_id=user_id,
                )

                processed_count += 1
                job.metadata["processed"] = processed_count
                job.save()

            except Exception as e:
                logger.error(f"Failed to process document {doc_id}: {e}")
                failed_count += 1
                job.metadata["failed"] = failed_count
                job.save()
                continue

        # Update final status
        job.progress = 100
        job.status = "completed"
        job.completed_at = timezone.now()
        job.result = {
            "total_documents": total_documents,
            "processed": processed_count,
            "failed": failed_count,
            "success_rate": (processed_count / total_documents) * 100
            if total_documents > 0
            else 0,
        }
        job.save()

        logger.info(
            f"Bulk entity extraction completed: {processed_count}/{total_documents} documents processed"
        )
        return job.result

    except Exception as e:
        logger.error(f"Bulk entity extraction task failed: {e}")

        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(
                f"Retrying bulk entity extraction (attempt {self.request.retries + 1})"
            )
            raise self.retry(exc=e)
        else:
            logger.error(
                f"Bulk entity extraction failed after {self.max_retries} retries"
            )
            raise


@shared_task
def cleanup_expired_cache():
    """Clean up expired cache entries related to LLM processing."""
    try:
        # This is a simple cleanup task - in production, you might want more sophisticated cache management
        cache.clear()
        logger.info("LLM processing cache cleared")
    except Exception as e:
        logger.error(f"Failed to cleanup cache: {e}")


@shared_task
def update_llm_usage_stats():
    """Update LLM usage statistics and cleanup old data."""
    try:
        # Update daily usage stats
        from django.db.models import Sum, Avg, Count
        from django.utils import timezone
        from datetime import timedelta

        # Get stats for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)

        # Update LLM model stats
        for llm_model in LLMModel.objects.all():
            recent_jobs = ProcessingJob.objects.filter(
                document__metadata__llm_model_used=llm_model.model_name,
                created_at__gte=thirty_days_ago,
            )

            if recent_jobs.exists():
                llm_model.daily_requests = recent_jobs.count()
                llm_model.daily_processing_time = (
                    recent_jobs.aggregate(
                        total_time=Sum("metadata__processing_time", default=0)
                    )["total_time"]
                    or 0
                )
                llm_model.save(
                    update_fields=["daily_requests", "daily_processing_time"]
                )

        logger.info("LLM usage statistics updated")

    except Exception as e:
        logger.error(f"Failed to update LLM usage stats: {e}")
