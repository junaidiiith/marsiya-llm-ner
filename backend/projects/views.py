from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from .models import Project, ProjectMembership
from .serializers import (
    ProjectSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectMembershipSerializer,
    ProjectStatsSerializer,
)
from .permissions import IsProjectMember, IsProjectAdmin, IsProjectOwner


class ProjectCreateView(generics.CreateAPIView):
    """Create a new project."""

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectCreateSerializer

    def perform_create(self, serializer):
        project = serializer.save(created_by=self.request.user)

        # Create owner membership
        ProjectMembership.objects.create(
            user=self.request.user,
            project=project,
            role="owner",
            can_edit_project=True,
            can_manage_members=True,
            can_upload_documents=True,
            can_edit_entities=True,
            can_export_data=True,
        )


class ProjectListView(generics.ListAPIView):
    """List projects for the authenticated user."""

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectListSerializer

    def get_queryset(self):
        user = self.request.user

        # Get projects where user is a member (excluding deleted projects)
        member_projects = Project.objects.filter(
            memberships__user=user, memberships__is_active=True, is_deleted=False
        ).distinct()

        # Get public projects (excluding deleted projects)
        public_projects = Project.objects.filter(
            is_public=True, allow_public_view=True, is_deleted=False
        ).exclude(id__in=member_projects.values_list("id", flat=True))

        # Combine and order by creation date
        all_projects = (member_projects | public_projects).order_by("-created_at")

        # Apply filters
        status_filter = self.request.query_params.get("status")
        if status_filter:
            all_projects = all_projects.filter(status=status_filter)

        research_area = self.request.query_params.get("research_area")
        if research_area:
            all_projects = all_projects.filter(research_area__icontains=research_area)

        is_public = self.request.query_params.get("is_public")
        if is_public is not None:
            is_public_bool = is_public.lower() == "true"
            all_projects = all_projects.filter(is_public=is_public_bool)

        return all_projects


class ProjectDetailView(generics.RetrieveAPIView):
    """Get project details."""

    permission_classes = [IsAuthenticated, IsProjectMember]
    serializer_class = ProjectDetailSerializer
    queryset = Project.objects.filter(is_deleted=False)
    lookup_field = "slug"


class ProjectUpdateView(generics.UpdateAPIView):
    """Update project details."""

    permission_classes = [IsAuthenticated, IsProjectAdmin]
    serializer_class = ProjectUpdateSerializer
    queryset = Project.objects.filter(is_deleted=False)
    lookup_field = "slug"

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class ProjectDeleteView(generics.DestroyAPIView):
    """Delete a project."""

    permission_classes = [IsAuthenticated, IsProjectOwner]
    queryset = Project.objects.filter(is_deleted=False)
    lookup_field = "slug"

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()


class ProjectMembershipListView(generics.ListAPIView):
    """List project members."""

    permission_classes = [IsAuthenticated, IsProjectMember]
    serializer_class = ProjectMembershipSerializer

    def get_queryset(self):
        project_slug = self.kwargs.get("project_slug")
        project = get_object_or_404(Project, slug=project_slug)
        return ProjectMembership.objects.filter(project=project, is_active=True)


class ProjectMembershipCreateView(generics.CreateAPIView):
    """Add a member to a project."""

    permission_classes = [IsAuthenticated, IsProjectAdmin]
    serializer_class = ProjectMembershipSerializer

    def perform_create(self, serializer):
        project_slug = self.kwargs.get("project_slug")
        project = get_object_or_404(Project, slug=project_slug)
        serializer.save(project=project)


class ProjectMembershipUpdateView(generics.UpdateAPIView):
    """Update project membership."""

    permission_classes = [IsAuthenticated, IsProjectAdmin]
    serializer_class = ProjectMembershipSerializer
    queryset = ProjectMembership.objects.all()

    def get_object(self):
        project_slug = self.kwargs.get("project_slug")
        membership_id = self.kwargs.get("pk")
        return get_object_or_404(
            ProjectMembership, id=membership_id, project__slug=project_slug
        )


class ProjectMembershipDeleteView(generics.DestroyAPIView):
    """Remove a member from a project."""

    permission_classes = [IsAuthenticated, IsProjectAdmin]
    queryset = ProjectMembership.objects.all()

    def get_object(self):
        project_slug = self.kwargs.get("project_slug")
        membership_id = self.kwargs.get("pk")
        return get_object_or_404(
            ProjectMembership, id=membership_id, project__slug=project_slug
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsProjectMember])
def project_stats(request, project_slug):
    """Get project statistics."""
    project = get_object_or_404(Project, slug=project_slug)

    # Document statistics
    total_documents = project.documents.count()
    processed_documents = project.documents.filter(
        processing_status="completed"
    ).count()
    pending_documents = project.documents.filter(processing_status="pending").count()

    # Entity statistics
    total_entities = project.documents.aggregate(total=Count("entities"))["total"] or 0

    verified_entities = (
        project.documents.aggregate(
            verified=Count("entities", filter=Q(entities__is_verified=True))
        )["verified"]
        or 0
    )

    # Member statistics
    total_members = project.memberships.filter(is_active=True).count()
    active_members = project.memberships.filter(
        is_active=True,
        user__last_activity__gte=timezone.now() - timezone.timedelta(days=30),
    ).count()

    # Processing statistics
    processing_jobs = project.processing_jobs.count()
    completed_jobs = project.processing_jobs.filter(status="completed").count()
    failed_jobs = project.processing_jobs.filter(status="failed").count()

    stats = {
        "total_documents": total_documents,
        "processed_documents": processed_documents,
        "pending_documents": pending_documents,
        "total_entities": total_entities,
        "verified_entities": verified_entities,
        "verification_rate": (verified_entities / total_entities * 100)
        if total_entities > 0
        else 0,
        "total_members": total_members,
        "active_members": active_members,
        "processing_jobs": processing_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "success_rate": (completed_jobs / processing_jobs * 100)
        if processing_jobs > 0
        else 0,
    }

    serializer = ProjectStatsSerializer(stats)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsProjectAdmin])
def project_archive(request, project_slug):
    """Archive a project."""
    project = get_object_or_404(Project, slug=project_slug)
    project.status = "completed"
    project.save()

    return Response({"message": "Project archived successfully"})


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsProjectAdmin])
def project_restore(request, project_slug):
    """Restore a deleted project."""
    project = get_object_or_404(Project, slug=project_slug)
    project.is_deleted = False
    project.deleted_at = None
    project.deleted_by = None
    project.save()

    return Response({"message": "Project restored successfully"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_projects(request):
    """Get all projects for the authenticated user."""
    user = request.user

    # Get projects where user is a member (excluding deleted projects)
    member_projects = Project.objects.filter(
        memberships__user=user, memberships__is_active=True, is_deleted=False
    )

    # Get projects created by user (excluding deleted projects)
    owned_projects = Project.objects.filter(created_by=user, is_deleted=False)

    # Combine and order by creation date - fix the distinct issue
    all_projects = (
        Project.objects.filter(
            Q(memberships__user=user, memberships__is_active=True) | Q(created_by=user),
            is_deleted=False,
        )
        .distinct()
        .order_by("-created_at")
    )

    serializer = ProjectListSerializer(all_projects, many=True)
    return Response(serializer.data)
