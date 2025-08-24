from rest_framework import permissions
from .models import Project, ProjectMembership


class IsProjectMember(permissions.BasePermission):
    """Allow access only to project members."""

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False

        # Allow superusers and staff users to do anything
        if request.user.is_superuser or request.user.is_staff:
            return True

        # For list views, allow access (filtering will be done in queryset)
        if hasattr(view, "action") and view.action == "list":
            return True

        # For other actions, check project membership
        project_slug = view.kwargs.get("project_slug") or view.kwargs.get("slug")
        if not project_slug:
            return False

        try:
            project = Project.objects.get(slug=project_slug)
            return ProjectMembership.objects.filter(
                user=request.user, project=project, is_active=True
            ).exists()
        except Project.DoesNotExist:
            return False


class IsProjectAdmin(permissions.BasePermission):
    """Allow access only to project administrators."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Allow superusers and staff users to do anything
        if request.user.is_superuser or request.user.is_staff:
            return True

        project_slug = view.kwargs.get("project_slug") or view.kwargs.get("slug")
        if not project_slug:
            return False

        try:
            project = Project.objects.get(slug=project_slug)
            membership = ProjectMembership.objects.filter(
                user=request.user, project=project, is_active=True
            ).first()

            if not membership:
                return False

            # Check if user has admin privileges
            return (
                membership.role in ["owner", "admin"]
                or membership.can_edit_project
                or membership.can_manage_members
            )
        except Project.DoesNotExist:
            return False


class IsProjectOwner(permissions.BasePermission):
    """Allow access only to project owners."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Allow superusers and staff users to do anything
        if request.user.is_superuser or request.user.is_staff:
            return True

        project_slug = view.kwargs.get("project_slug") or view.kwargs.get("slug")
        if not project_slug:
            return False

        try:
            project = Project.objects.get(slug=project_slug)
            membership = ProjectMembership.objects.filter(
                user=request.user, project=project, is_active=True
            ).first()

            if not membership:
                return False

            # Check if user is owner
            return membership.role == "owner"
        except Project.DoesNotExist:
            return False


class CanUploadDocuments(permissions.BasePermission):
    """Allow document upload only to users with permission."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Allow superusers and staff users to do anything
        if request.user.is_superuser or request.user.is_staff:
            return True

        project_slug = view.kwargs.get("project_slug")
        if not project_slug:
            return False

        try:
            project = Project.objects.get(slug=project_slug)
            membership = ProjectMembership.objects.filter(
                user=request.user, project=project, is_active=True
            ).first()

            if not membership:
                return False

            return membership.can_upload_documents
        except Project.DoesNotExist:
            return False


class CanEditEntities(permissions.BasePermission):
    """Allow entity editing only to users with permission."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Allow superusers and staff users to do anything
        if request.user.is_superuser or request.user.is_staff:
            return True

        project_slug = view.kwargs.get("project_slug")
        if not project_slug:
            return False

        try:
            project = Project.objects.get(slug=project_slug)
            membership = ProjectMembership.objects.filter(
                user=request.user, project=project, is_active=True
            ).first()

            if not membership:
                return False

            return membership.can_edit_entities
        except Project.DoesNotExist:
            return False


class CanExportData(permissions.BasePermission):
    """Allow data export only to users with permission."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Allow superusers and staff users to do anything
        if request.user.is_superuser or request.user.is_staff:
            return True

        project_slug = view.kwargs.get("project_slug")
        if not project_slug:
            return False

        try:
            project = Project.objects.get(slug=project_slug)
            membership = ProjectMembership.objects.filter(
                user=request.user, project=project, is_active=True
            ).first()

            if not membership:
                return False

            return membership.can_export_data
        except Project.DoesNotExist:
            return False
