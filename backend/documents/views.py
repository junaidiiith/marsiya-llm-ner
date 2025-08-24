from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from .models import Document, DocumentVersion
from .serializers import (
    DocumentSerializer,
    DocumentCreateSerializer,
    DocumentUpdateSerializer,
    DocumentDetailSerializer,
    DocumentListSerializer,
    DocumentVersionSerializer,
    DocumentUploadSerializer,
    DocumentProcessingSerializer,
    DocumentStatsSerializer,
)
from projects.permissions import IsProjectMember, CanUploadDocuments

from processing.tasks import process_document_with_llm
from projects.models import Project


class DocumentCreateView(generics.CreateAPIView):
    """Create a new document."""

    permission_classes = [IsAuthenticated, CanUploadDocuments]
    serializer_class = DocumentCreateSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        document = serializer.save(created_by=self.request.user)

        # Create initial version
        DocumentVersion.objects.create(
            document=document,
            version_number=1,
            content=document.content,
            changed_by=self.request.user,
        )


class DocumentListView(generics.ListAPIView):
    """List documents for a project."""

    permission_classes = [IsAuthenticated, IsProjectMember]
    serializer_class = DocumentListSerializer

    def get_queryset(self):
        project_slug = self.kwargs.get("project_slug")
        project = get_object_or_404(Project, slug=project_slug)

        queryset = Document.objects.filter(project=project, is_deleted=False)

        # Apply filters
        status_filter = self.request.query_params.get("processing_status")
        if status_filter:
            queryset = queryset.filter(processing_status=status_filter)

        language = self.request.query_params.get("language")
        if language:
            queryset = queryset.filter(language=language)

        verified_only = self.request.query_params.get("verified_only")
        if verified_only and verified_only.lower() == "true":
            queryset = queryset.filter(verified_entities__gt=0)

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(content__icontains=search)
                | Q(description__icontains=search)
            )

        return queryset.order_by("-created_at")


class DocumentDetailView(generics.RetrieveAPIView):
    """Get document details."""

    permission_classes = [IsAuthenticated, IsProjectMember]
    serializer_class = DocumentDetailSerializer
    queryset = Document.objects.filter(is_deleted=False)

    def get_object(self):
        project_slug = self.kwargs.get("project_slug")
        document_id = self.kwargs.get("pk")
        return get_object_or_404(
            Document, id=document_id, project__slug=project_slug, is_deleted=False
        )


class DocumentUpdateView(generics.UpdateAPIView):
    """Update document details."""

    permission_classes = [IsAuthenticated, IsProjectMember]
    serializer_class = DocumentUpdateSerializer
    queryset = Document.objects.filter(is_deleted=False)

    def get_object(self):
        project_slug = self.kwargs.get("project_slug")
        document_id = self.kwargs.get("pk")
        return get_object_or_404(
            Document, id=document_id, project__slug=project_slug, is_deleted=False
        )

    def perform_update(self, serializer):
        document = serializer.save(updated_by=self.request.user)

        # Create new version if content changed
        if "content" in serializer.validated_data:
            current_version = document.versions.order_by("-version_number").first()
            new_version_number = (
                (current_version.version_number + 1) if current_version else 1
            )

            DocumentVersion.objects.create(
                document=document,
                version_number=new_version_number,
                content=document.content,
                changed_by=self.request.user,
                change_summary=f"Updated by {self.request.user.username}",
            )


class DocumentDeleteView(generics.DestroyAPIView):
    """Delete a document."""

    permission_classes = [IsAuthenticated, IsProjectMember]
    queryset = Document.objects.filter(is_deleted=False)

    def get_object(self):
        project_slug = self.kwargs.get("project_slug")
        document_id = self.kwargs.get("pk")
        return get_object_or_404(
            Document, id=document_id, project__slug=project_slug, is_deleted=False
        )

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()


class DocumentVersionListView(generics.ListAPIView):
    """List document versions."""

    permission_classes = [IsAuthenticated, IsProjectMember]
    serializer_class = DocumentVersionSerializer

    def get_queryset(self):
        project_slug = self.kwargs.get("project_slug")
        document_id = self.kwargs.get("document_pk")
        return DocumentVersion.objects.filter(
            document__id=document_id, document__project__slug=project_slug
        ).order_by("-version_number")


class DocumentVersionDetailView(generics.RetrieveAPIView):
    """Get document version details."""

    permission_classes = [IsAuthenticated, IsProjectMember]
    serializer_class = DocumentVersionSerializer
    queryset = DocumentVersion.objects.all()

    def get_object(self):
        project_slug = self.kwargs.get("project_slug")
        document_id = self.kwargs.get("document_pk")
        version_id = self.kwargs.get("pk")
        return get_object_or_404(
            DocumentVersion,
            id=version_id,
            document__id=document_id,
            document__project__slug=project_slug,
        )


class DocumentUploadView(generics.CreateAPIView):
    """Upload a document file."""

    permission_classes = [IsAuthenticated, CanUploadDocuments]
    serializer_class = DocumentUploadSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        document = serializer.save(created_by=self.request.user)

        # Create initial version
        DocumentVersion.objects.create(
            document=document,
            version_number=1,
            content=document.content,
            changed_by=self.request.user,
        )


class DocumentProcessingView(generics.GenericAPIView):
    """Process document with LLM for entity extraction."""

    permission_classes = [IsAuthenticated, IsProjectMember]
    serializer_class = DocumentProcessingSerializer

    def post(self, request, project_slug, pk):
        document = get_object_or_404(Document, id=pk, project__slug=project_slug)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Start LLM processing
        prompt_type = serializer.validated_data.get("prompt_type", "marsiya")

        # Start the processing task
        task = process_document_with_llm.delay(
            document_id=document.id, prompt_type=prompt_type, user_id=request.user.id
        )

        # Update document status
        document.processing_status = "processing"
        document.processing_started_at = timezone.now()
        document.save()

        return Response(
            {
                "message": "Document processing started successfully",
                "document_id": document.id,
                "task_id": task.id,
                "prompt_type": prompt_type,
            }
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsProjectMember])
def document_stats(request, project_slug, pk):
    """Get document statistics."""
    document = get_object_or_404(Document, id=pk, project__slug=project_slug)

    # Entity statistics
    total_entities = document.entities.count()
    verified_entities = document.entities.filter(is_verified=True).count()
    unverified_entities = total_entities - verified_entities

    # Entity type distribution
    entity_type_stats = (
        document.entities.values("entity_type__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Confidence score statistics
    confidence_stats = document.entities.aggregate(
        avg_confidence=Avg("confidence_score"),
        min_confidence=Avg("confidence_score"),
        max_confidence=Avg("confidence_score"),
    )

    # Processing statistics
    processing_duration = None
    if document.processing_completed_at and document.processing_started_at:
        processing_duration = (
            document.processing_completed_at - document.processing_started_at
        )

    stats = {
        "total_entities": total_entities,
        "verified_entities": verified_entities,
        "unverified_entities": unverified_entities,
        "verification_rate": (verified_entities / total_entities * 100)
        if total_entities > 0
        else 0,
        "entity_type_distribution": list(entity_type_stats),
        "confidence_stats": confidence_stats,
        "processing_duration": processing_duration,
        "word_count": document.word_count,
        "character_count": document.character_count,
        "line_count": document.line_count,
        "total_versions": document.versions.count(),
    }

    serializer = DocumentStatsSerializer(stats)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsProjectMember])
def document_restore(request, project_slug, pk):
    """Restore a deleted document."""
    document = get_object_or_404(Document, id=pk, project__slug=project_slug)

    document.is_deleted = False
    document.deleted_at = None
    document.deleted_by = None
    document.save()

    return Response({"message": "Document restored successfully"})


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsProjectMember])
def document_search(request, project_slug):
    """Search documents within a project."""
    project = get_object_or_404(Project, slug=project_slug)

    query = request.query_params.get("q", "")
    if not query:
        return Response(
            {"error": "Search query is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    documents = Document.objects.filter(
        Q(title__icontains=query)
        | Q(content__icontains=query)
        | Q(description__icontains=query),
        project=project,
    ).order_by("-created_at")

    serializer = DocumentListSerializer(documents, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsProjectMember])
def document_bulk_action(request, project_slug):
    """Perform bulk actions on documents."""
    project = get_object_or_404(Project, slug=project_slug)

    action = request.data.get("action")
    document_ids = request.data.get("document_ids", [])

    if not action or not document_ids:
        return Response(
            {"error": "Action and document_ids are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    documents = Document.objects.filter(id__in=document_ids, project=project)

    if action == "delete":
        for document in documents:
            document.is_deleted = True
            document.deleted_at = timezone.now()
            document.deleted_by = request.user
            document.save()
        message = f"{documents.count()} documents deleted"

    elif action == "archive":
        for document in documents:
            document.processing_status = "completed"
            document.save()
        message = f"{documents.count()} documents archived"

    elif action == "process":
        for document in documents:
            if document.processing_status == "pending":
                document.processing_status = "processing"
                document.processing_started_at = timezone.now()
                document.save()
        message = f"{documents.count()} documents queued for processing"

    else:
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": message, "affected_count": documents.count()})
