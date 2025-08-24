from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from .models import Entity, EntityType, EntityRelationship
from .serializers import (
    EntitySerializer,
    EntityCreateSerializer,
    EntityUpdateSerializer,
    EntityListSerializer,
    EntityTypeSerializer,
    EntityTypeCreateSerializer,
    EntityTypeUpdateSerializer,
    EntityVerificationSerializer,
    EntityBulkUpdateSerializer,
    EntityRelationshipSerializer,
    EntityRelationshipCreateSerializer,
    EntityRelationshipUpdateSerializer,
    EntitySearchSerializer,
    EntityStatsSerializer,
)
from projects.permissions import IsProjectMember, CanEditEntities
from documents.models import Document
from projects.models import Project


class EntityTypeListView(generics.ListAPIView):
    """List all entity types."""

    permission_classes = [IsAuthenticated]
    serializer_class = EntityTypeSerializer
    queryset = EntityType.objects.filter(is_active=True).order_by("sort_order")


class EntityTypeCreateView(generics.CreateAPIView):
    """Create a new entity type."""

    permission_classes = [IsAuthenticated]
    serializer_class = EntityTypeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EntityTypeUpdateView(generics.UpdateAPIView):
    """Update an entity type."""

    permission_classes = [IsAuthenticated]
    serializer_class = EntityTypeUpdateSerializer
    queryset = EntityType.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class EntityListView(generics.ListAPIView):
    """List entities for a document."""

    permission_classes = [IsAuthenticated, IsProjectMember]
    serializer_class = EntityListSerializer

    def get_queryset(self):
        project_slug = self.kwargs.get("project_slug")
        document_id = self.kwargs.get("document_pk")

        # Verify document belongs to project
        document = get_object_or_404(
            Document, id=document_id, project__slug=project_slug
        )

        queryset = Entity.objects.filter(document=document)

        # Apply filters
        entity_type = self.request.query_params.get("entity_type")
        if entity_type:
            queryset = queryset.filter(entity_type__name=entity_type)

        is_verified = self.request.query_params.get("is_verified")
        if is_verified is not None:
            is_verified_bool = is_verified.lower() == "true"
            queryset = queryset.filter(is_verified=is_verified_bool)

        source = self.request.query_params.get("source")
        if source:
            queryset = queryset.filter(source=source)

        confidence_min = self.request.query_params.get("confidence_min")
        if confidence_min:
            queryset = queryset.filter(confidence_score__gte=float(confidence_min))

        confidence_max = self.request.query_params.get("confidence_max")
        if confidence_max:
            queryset = queryset.filter(confidence_score__lte=float(confidence_max))

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(text__icontains=search)
                | Q(context_before__icontains=search)
                | Q(context_after__icontains=search)
            )

        return queryset.order_by("line_number", "word_position")


class EntityDetailView(generics.RetrieveAPIView):
    """Get entity details."""

    permission_classes = [IsAuthenticated, IsProjectMember]
    serializer_class = EntitySerializer
    queryset = Entity.objects.all()

    def get_object(self):
        project_slug = self.kwargs.get("project_slug")
        document_id = self.kwargs.get("document_pk")
        entity_id = self.kwargs.get("pk")

        return get_object_or_404(
            Entity,
            id=entity_id,
            document__id=document_id,
            document__project__slug=project_slug,
        )


class EntityCreateView(generics.CreateAPIView):
    """Create a new entity."""

    permission_classes = [IsAuthenticated, CanEditEntities]
    serializer_class = EntityCreateSerializer

    def perform_create(self, serializer):
        entity = serializer.save(created_by=self.request.user, source="manual")


class EntityUpdateView(generics.UpdateAPIView):
    """Update an entity."""

    permission_classes = [IsAuthenticated, CanEditEntities]
    serializer_class = EntityUpdateSerializer
    queryset = Entity.objects.all()

    def get_object(self):
        project_slug = self.kwargs.get("project_slug")
        document_id = self.kwargs.get("document_pk")
        entity_id = self.kwargs.get("pk")

        return get_object_or_404(
            Entity,
            id=entity_id,
            document__id=document_id,
            document__project__slug=project_slug,
        )

    def perform_update(self, serializer):
        entity = serializer.save(updated_by=self.request.user)

        # Update document entity counts
        document = entity.document
        document.total_entities = document.entities.count()
        document.verified_entities = document.entities.filter(is_verified=True).count()
        document.unverified_entities = (
            document.total_entities - document.verified_entities
        )
        document.save()


class EntityDeleteView(generics.DestroyAPIView):
    """Delete an entity."""

    permission_classes = [IsAuthenticated, CanEditEntities]
    queryset = Entity.objects.all()

    def get_object(self):
        project_slug = self.kwargs.get("project_slug")
        document_id = self.kwargs.get("document_pk")
        entity_id = self.kwargs.get("pk")

        return get_object_or_404(
            Entity,
            id=entity_id,
            document__id=document_id,
            document__project__slug=project_slug,
        )

    def perform_destroy(self, instance):
        document = instance.document
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()

        # Update document entity counts
        document.total_entities = document.entities.count()
        document.verified_entities = document.entities.filter(is_verified=True).count()
        document.unverified_entities = (
            document.total_entities - document.verified_entities
        )
        document.save()


class EntityVerificationView(generics.UpdateAPIView):
    """Verify an entity."""

    permission_classes = [IsAuthenticated, CanEditEntities]
    serializer_class = EntityVerificationSerializer
    queryset = Entity.objects.all()

    def get_object(self):
        project_slug = self.kwargs.get("project_slug")
        document_id = self.kwargs.get("document_pk")
        entity_id = self.kwargs.get("pk")

        return get_object_or_404(
            Entity,
            id=entity_id,
            document__id=document_id,
            document__project__slug=project_slug,
        )

    def perform_update(self, serializer):
        entity = serializer.save(
            verified_by=self.request.user, verified_at=timezone.now()
        )

        # Update document entity counts
        document = entity.document
        document.verified_entities = document.entities.filter(is_verified=True).count()
        document.unverified_entities = (
            document.total_entities - document.verified_entities
        )
        document.save()


class EntityBulkUpdateView(generics.GenericAPIView):
    """Bulk update entities."""

    permission_classes = [IsAuthenticated, CanEditEntities]
    serializer_class = EntityBulkUpdateSerializer

    def post(self, request, project_slug, document_pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        entity_ids = serializer.validated_data["entity_ids"]
        updates = serializer.validated_data["updates"]

        # Verify all entities belong to the document
        entities = Entity.objects.filter(
            id__in=entity_ids,
            document__id=document_pk,
            document__project__slug=project_slug,
        )

        if len(entities) != len(entity_ids):
            return Response(
                {"error": "Some entities not found or access denied"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Apply updates
        updated_count = 0
        for entity in entities:
            for field, value in updates.items():
                if hasattr(entity, field):
                    setattr(entity, field, value)

            entity.updated_by = request.user
            entity.save()
            updated_count += 1

        return Response(
            {
                "message": f"{updated_count} entities updated successfully",
                "updated_count": updated_count,
            }
        )


class EntityRelationshipListView(generics.ListAPIView):
    """List entity relationships."""

    permission_classes = [IsAuthenticated, IsProjectMember]
    serializer_class = EntityRelationshipSerializer

    def get_queryset(self):
        project_slug = self.kwargs.get("project_slug")
        document_id = self.kwargs.get("document_pk")

        # Verify document belongs to project
        document = get_object_or_404(
            Document, id=document_id, project__slug=project_slug
        )

        return EntityRelationship.objects.filter(
            Q(source_entity__document=document) | Q(target_entity__document=document)
        )


class EntityRelationshipCreateView(generics.CreateAPIView):
    """Create a new entity relationship."""

    permission_classes = [IsAuthenticated, CanEditEntities]
    serializer_class = EntityRelationshipCreateSerializer


class EntityRelationshipUpdateView(generics.UpdateAPIView):
    """Update an entity relationship."""

    permission_classes = [IsAuthenticated, CanEditEntities]
    serializer_class = EntityRelationshipUpdateSerializer
    queryset = EntityRelationship.objects.all()


class EntityRelationshipDeleteView(generics.DestroyAPIView):
    """Delete an entity relationship."""

    permission_classes = [IsAuthenticated, CanEditEntities]
    queryset = EntityRelationship.objects.all()


class EntitySearchView(generics.GenericAPIView):
    """Search entities across documents."""

    permission_classes = [IsAuthenticated, IsProjectMember]
    serializer_class = EntitySearchSerializer

    def post(self, request, project_slug):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data["query"]
        entity_types = serializer.validated_data.get("entity_types", [])
        is_verified = serializer.validated_data.get("is_verified")

        # Get project
        project = get_object_or_404(Project, slug=project_slug)

        # Build query
        queryset = Entity.objects.filter(document__project=project)

        if query:
            queryset = queryset.filter(
                Q(text__icontains=query)
                | Q(context_before__icontains=query)
                | Q(context_after__icontains=query)
            )

        if entity_types:
            queryset = queryset.filter(entity_type__name__in=entity_types)

        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified)

        # Order by relevance (could be enhanced with search ranking)
        entities = queryset.order_by("-confidence_score", "-created_at")

        # Serialize results
        entity_serializer = EntityListSerializer(entities, many=True)

        return Response(
            {
                "query": query,
                "results": entity_serializer.data,
                "total_count": entities.count(),
            }
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsProjectMember])
def entity_stats(request, project_slug, document_pk):
    """Get entity statistics for a document."""
    document = get_object_or_404(Document, id=document_pk, project__slug=project_slug)

    # Entity type distribution
    entity_type_stats = (
        document.entities.values("entity_type__name")
        .annotate(
            count=Count("id"),
            verified_count=Count("id", filter=Q(is_verified=True)),
            unverified_count=Count("id", filter=Q(is_verified=False)),
        )
        .order_by("-count")
    )

    # Source distribution
    source_stats = (
        document.entities.values("source")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Confidence score statistics
    confidence_stats = document.entities.aggregate(
        avg_confidence=Avg("confidence_score"),
        min_confidence=Avg("confidence_score"),
        max_confidence=Avg("confidence_score"),
    )

    # Verification statistics
    verification_stats = document.entities.aggregate(
        total=Count("id"),
        verified=Count("id", filter=Q(is_verified=True)),
        unverified=Count("id", filter=Q(is_verified=False)),
    )

    # Line distribution
    line_stats = (
        document.entities.values("line_number")
        .annotate(count=Count("id"))
        .order_by("line_number")
    )

    stats = {
        "entity_type_distribution": list(entity_type_stats),
        "source_distribution": list(source_stats),
        "confidence_stats": confidence_stats,
        "verification_stats": verification_stats,
        "line_distribution": list(line_stats),
        "total_entities": verification_stats["total"],
        "verified_entities": verification_stats["verified"],
        "unverified_entities": verification_stats["unverified"],
        "verification_rate": (
            verification_stats["verified"] / verification_stats["total"] * 100
        )
        if verification_stats["total"] > 0
        else 0,
    }

    serializer = EntityStatsSerializer(stats)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, CanEditEntities])
def entity_bulk_verify(request, project_slug, document_pk):
    """Bulk verify entities."""
    entity_ids = request.data.get("entity_ids", [])

    if not entity_ids:
        return Response(
            {"error": "Entity IDs are required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Verify all entities belong to the document
    entities = Entity.objects.filter(
        id__in=entity_ids,
        document__id=document_pk,
        document__project__slug=project_slug,
    )

    if len(entities) != len(entity_ids):
        return Response(
            {"error": "Some entities not found or access denied"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Verify entities
    verified_count = 0
    for entity in entities:
        if not entity.is_verified:
            entity.is_verified = True
            entity.verified_by = request.user
            entity.verified_at = timezone.now()
            entity.save()
            verified_count += 1

    # Update document entity counts
    document = entities.first().document
    document.verified_entities = document.entities.filter(is_verified=True).count()
    document.unverified_entities = document.total_entities - document.verified_entities
    document.save()

    return Response(
        {
            "message": f"{verified_count} entities verified successfully",
            "verified_count": verified_count,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, CanEditEntities])
def entity_bulk_delete(request, project_slug, document_pk):
    """Bulk delete entities."""
    entity_ids = request.data.get("entity_ids", [])

    if not entity_ids:
        return Response(
            {"error": "Entity IDs are required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Verify all entities belong to the document
    entities = Entity.objects.filter(
        id__in=entity_ids,
        document__id=document_pk,
        document__project__slug=project_slug,
    )

    if len(entities) != len(entity_ids):
        return Response(
            {"error": "Some entities not found or access denied"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Delete entities
    deleted_count = 0
    for entity in entities:
        entity.is_deleted = True
        entity.deleted_at = timezone.now()
        entity.deleted_by = request.user
        entity.save()
        deleted_count += 1

    # Update document entity counts
    document = entities.first().document
    document.total_entities = document.entities.count()
    document.verified_entities = document.entities.filter(is_verified=True).count()
    document.unverified_entities = document.total_entities - document.verified_entities
    document.save()

    return Response(
        {
            "message": f"{deleted_count} entities deleted successfully",
            "deleted_count": deleted_count,
        }
    )
