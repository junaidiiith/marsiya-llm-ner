import logging
from typing import Dict, List, Any
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from .models import ProcessingJob
from documents.models import Document
from entities.models import Entity
from llm_integration.tasks import extract_entities_from_text

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_with_llm(
    self, document_id: int, prompt_type: str = "marsiya", user_id: int = None
):
    """
    Process a document with LLM for entity extraction.

    Args:
        document_id: ID of the document to process
        prompt_type: Type of prompt to use
        user_id: ID of the user requesting the processing
    """
    try:
        # Get the document
        document = Document.objects.get(id=document_id)

        # Create or update processing job
        job, created = ProcessingJob.objects.get_or_create(
            document=document,
            job_type="llm_processing",
            defaults={
                "status": "processing",
                "progress": 0,
                "created_by_id": user_id,
                "metadata": {"prompt_type": prompt_type, "processing_method": "llm"},
            },
        )

        if not created:
            job.status = "processing"
            job.progress = 0
            job.started_at = timezone.now()
            job.metadata.update(
                {"prompt_type": prompt_type, "processing_method": "llm"}
            )
            job.save()

        # Update progress
        job.progress = 10
        job.save()

        # Get document text
        if document.file:
            # Read from file
            try:
                with document.file.open("r", encoding="utf-8") as f:
                    text = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                with document.file.open("r", encoding="latin-1") as f:
                    text = f.read()
        else:
            # Use content field
            text = document.content or ""

        if not text.strip():
            raise ValueError("Document has no readable text content")

        job.progress = 20
        job.save()

        # Process with LLM
        try:
            # Call the LLM entity extraction task
            llm_task = extract_entities_from_text.delay(
                text=text,
                document_id=document_id,
                prompt_type=prompt_type,
                user_id=user_id,
            )

            # Update job with LLM task ID
            job.metadata["llm_task_id"] = llm_task.id
            job.progress = 50
            job.save()

            # Wait for LLM task to complete
            result = llm_task.get(timeout=300)  # 5 minutes timeout

            job.progress = 100
            job.status = "completed"
            job.completed_at = timezone.now()
            job.result = result
            job.save()

            logger.info(f"Document {document_id} processed successfully with LLM")
            return result

        except Exception as e:
            logger.error(f"LLM processing failed for document {document_id}: {e}")
            job.status = "failed"
            job.error_message = f"LLM processing failed: {str(e)}"
            job.completed_at = timezone.now()
            job.save()
            raise

    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")
        raise
    except Exception as e:
        logger.error(f"Document processing task failed: {e}")

        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(
                f"Retrying document processing (attempt {self.request.retries + 1})"
            )
            raise self.retry(exc=e)
        else:
            logger.error(f"Document processing failed after {self.max_retries} retries")
            raise


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def cancel_processing_job(self, job_id: int):
    """
    Cancel a processing job.

    Args:
        job_id: ID of the job to cancel
    """
    try:
        job = ProcessingJob.objects.get(id=job_id)

        if job.status in ["completed", "failed", "cancelled"]:
            logger.warning(f"Job {job_id} cannot be cancelled (status: {job.status})")
            return False

        # Cancel the job
        job.status = "cancelled"
        job.cancelled_at = timezone.now()
        job.metadata["cancelled_by"] = "system"
        job.save()

        # If there's an associated LLM task, try to revoke it
        if "llm_task_id" in job.metadata:
            try:
                from celery.result import AsyncResult

                llm_task = AsyncResult(job.metadata["llm_task_id"])
                if llm_task.state in ["PENDING", "STARTED"]:
                    llm_task.revoke(terminate=True)
                    logger.info(f"LLM task {job.metadata['llm_task_id']} revoked")
            except Exception as e:
                logger.warning(f"Failed to revoke LLM task: {e}")

        logger.info(f"Processing job {job_id} cancelled successfully")
        return True

    except ProcessingJob.DoesNotExist:
        logger.error(f"Processing job {job_id} not found")
        raise
    except Exception as e:
        logger.error(f"Failed to cancel processing job {job_id}: {e}")

        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(
                f"Retrying job cancellation (attempt {self.request.retries + 1})"
            )
            raise self.retry(exc=e)
        else:
            logger.error(f"Job cancellation failed after {self.max_retries} retries")
            raise


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def retry_processing_job(self, job_id: int):
    """
    Retry a failed processing job.

    Args:
        job_id: ID of the job to retry
    """
    try:
        job = ProcessingJob.objects.get(id=job_id)

        if job.status != "failed":
            logger.warning(f"Job {job_id} cannot be retried (status: {job.status})")
            return False

        # Reset job for retry
        job.status = "pending"
        job.progress = 0
        job.started_at = None
        job.completed_at = None
        job.cancelled_at = None
        job.error_message = None
        job.metadata["retry_count"] = job.metadata.get("retry_count", 0) + 1
        job.metadata["retry_attempt"] = timezone.now().isoformat()
        job.save()

        # Re-queue the job based on its type
        if job.job_type == "llm_processing":
            # Re-queue LLM processing
            process_document_with_llm.delay(
                document_id=job.document.id,
                prompt_type=job.metadata.get("prompt_type", "marsiya"),
                user_id=job.created_by_id,
            )
        elif job.job_type == "entity_extraction":
            # Re-queue entity extraction
            extract_entities_from_text.delay(
                text="",  # Will be fetched from document
                document_id=job.document.id,
                prompt_type=job.metadata.get("prompt_type", "marsiya"),
                user_id=job.created_by_id,
            )
        else:
            logger.warning(f"Unknown job type for retry: {job.job_type}")
            return False

        logger.info(f"Processing job {job_id} queued for retry")
        return True

    except ProcessingJob.DoesNotExist:
        logger.error(f"Processing job {job_id} not found")
        raise
    except Exception as e:
        logger.error(f"Failed to retry processing job {job_id}: {e}")

        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job retry (attempt {self.request.retries + 1})")
            raise self.retry(exc=e)
        else:
            logger.error(f"Job retry failed after {self.max_retries} retries")
            raise


@shared_task
def cleanup_old_jobs():
    """Clean up old completed/failed processing jobs."""
    try:
        from django.utils import timezone
        from datetime import timedelta

        # Keep jobs for 90 days
        cutoff_date = timezone.now() - timedelta(days=90)

        # Get old jobs
        old_jobs = ProcessingJob.objects.filter(
            created_at__lt=cutoff_date, status__in=["completed", "failed", "cancelled"]
        )

        count = old_jobs.count()
        old_jobs.delete()

        logger.info(f"Cleaned up {count} old processing jobs")
        return count

    except Exception as e:
        logger.error(f"Failed to cleanup old jobs: {e}")
        return 0


@shared_task
def send_processing_notifications():
    """Send email notifications for completed/failed processing jobs."""
    try:
        from django.core.mail import send_mail
        from django.conf import settings

        # Get jobs that need notifications
        jobs_to_notify = ProcessingJob.objects.filter(
            notification_sent=False,
            status__in=["completed", "failed"],
            created_by__isnull=False,
        ).select_related("created_by", "document")

        for job in jobs_to_notify:
            try:
                user = job.created_by
                subject = f"Processing Job {job.status.title()}: {job.document.title}"

                if job.status == "completed":
                    message = f"""
Hello {user.get_full_name() or user.username},

Your document "{job.document.title}" has been processed successfully.

Job Details:
- Job ID: {job.id}
- Document: {job.document.title}
- Status: {job.status}
- Completed: {job.completed_at}
- Entities Extracted: {job.result.get("entities_extracted", 0) if job.result else "N/A"}

You can view the results in your dashboard.

Best regards,
Marsiya NER Team
"""
                else:  # failed
                    message = f"""
Hello {user.get_full_name() or user.username},

Your document "{job.document.title}" processing has failed.

Job Details:
- Job ID: {job.id}
- Document: {job.document.title}
- Status: {job.status}
- Error: {job.error_message or "Unknown error"}

Please try again or contact support if the issue persists.

Best regards,
Marsiya NER Team
"""

                # Send email
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )

                # Mark notification as sent
                job.notification_sent = True
                job.save(update_fields=["notification_sent"])

                logger.info(f"Notification sent for job {job.id}")

            except Exception as e:
                logger.error(f"Failed to send notification for job {job.id}: {e}")
                continue

        logger.info("Processing notifications sent")

    except Exception as e:
        logger.error(f"Failed to send processing notifications: {e}")


@shared_task
def update_processing_stats():
    """Update processing statistics and metrics."""
    try:
        from django.db.models import Count, Avg, Sum
        from django.utils import timezone
        from datetime import timedelta

        # Get stats for the last 24 hours
        yesterday = timezone.now() - timedelta(days=1)

        # Daily processing stats
        daily_stats = ProcessingJob.objects.filter(created_at__gte=yesterday).aggregate(
            total_jobs=Count("id"),
            completed_jobs=Count("id", filter={"status": "completed"}),
            failed_jobs=Count("id", filter={"status": "failed"}),
            cancelled_jobs=Count("id", filter={"status": "cancelled"}),
            avg_processing_time=Avg("metadata__processing_time"),
        )

        # Update cache with daily stats
        from django.core.cache import cache

        cache.set("daily_processing_stats", daily_stats, timeout=3600)  # 1 hour

        # Update job performance metrics
        for job_type in [
            "llm_processing",
            "entity_extraction",
            "bulk_entity_extraction",
        ]:
            type_stats = ProcessingJob.objects.filter(
                job_type=job_type, created_at__gte=yesterday
            ).aggregate(
                total=Count("id"),
                completed=Count("id", filter={"status": "completed"}),
                failed=Count("id", filter={"status": "failed"}),
                avg_time=Avg("metadata__processing_time"),
            )

            cache.set(f"job_type_stats_{job_type}", type_stats, timeout=3600)

        logger.info("Processing statistics updated")
        return daily_stats

    except Exception as e:
        logger.error(f"Failed to update processing stats: {e}")
        return None


@shared_task
def monitor_processing_queue():
    """Monitor the processing queue and alert on issues."""
    try:
        from django.db.models import Count
        from django.core.cache import cache

        # Check for stuck jobs (processing for more than 1 hour)
        one_hour_ago = timezone.now() - timedelta(hours=1)
        stuck_jobs = ProcessingJob.objects.filter(
            status="processing", started_at__lt=one_hour_ago
        ).count()

        # Check for failed jobs in the last hour
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_failures = ProcessingJob.objects.filter(
            status="failed", created_at__gte=one_hour_ago
        ).count()

        # Check queue length
        pending_jobs = ProcessingJob.objects.filter(status="pending").count()
        processing_jobs = ProcessingJob.objects.filter(status="processing").count()

        # Store monitoring data
        monitoring_data = {
            "stuck_jobs": stuck_jobs,
            "recent_failures": recent_failures,
            "pending_jobs": pending_jobs,
            "processing_jobs": processing_jobs,
            "timestamp": timezone.now().isoformat(),
        }

        cache.set(
            "processing_queue_monitor", monitoring_data, timeout=1800
        )  # 30 minutes

        # Alert if there are issues
        if stuck_jobs > 5:
            logger.warning(f"High number of stuck jobs: {stuck_jobs}")

        if recent_failures > 10:
            logger.warning(f"High number of recent failures: {recent_failures}")

        if pending_jobs > 100:
            logger.warning(f"Large processing queue: {pending_jobs} pending jobs")

        logger.info("Processing queue monitoring completed")
        return monitoring_data

    except Exception as e:
        logger.error(f"Failed to monitor processing queue: {e}")
        return None
