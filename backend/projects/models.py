from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from core.models import UserStampedModel, SoftDeleteModel


class Project(UserStampedModel, SoftDeleteModel):
    """Research project for organizing documents and collaboration."""

    # Basic Information
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)

    # Project Details
    research_area = models.CharField(max_length=200, blank=True)
    methodology = models.TextField(blank=True)
    objectives = models.JSONField(default=list)
    timeline = models.JSONField(default=dict)

    # Collaboration
    users = models.ManyToManyField(
        "users.User", through="ProjectMembership", related_name="projects"
    )

    # Project Status
    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("on_hold", "On Hold"),
        ("cancelled", "Cancelled"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planning")

    # Access Control
    is_public = models.BooleanField(default=False)
    allow_public_view = models.BooleanField(default=False)

    # Metadata
    tags = models.JSONField(default=list)
    references = models.JSONField(default=list)

    class Meta:
        db_table = "projects_project"
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["is_public"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_members_count(self):
        """Get total number of project members."""
        return self.users.count()

    def get_documents_count(self):
        """Get total number of documents in project."""
        return self.documents.filter(is_deleted=False).count()

    def get_entities_count(self):
        """Get total number of entities across all documents."""
        total = 0
        for doc in self.documents.filter(is_deleted=False):
            total += doc.total_entities
        return total

    def get_verified_entities_count(self):
        """Get total number of verified entities."""
        total = 0
        for doc in self.documents.filter(is_deleted=False):
            total += doc.verified_entities
        return total

    def add_member(self, user, role="researcher"):
        """Add user to project with specified role."""
        membership, created = ProjectMembership.objects.get_or_create(
            user=user, project=self, defaults={"role": role}
        )
        return membership

    def remove_member(self, user):
        """Remove user from project."""
        try:
            membership = ProjectMembership.objects.get(user=user, project=self)
            membership.delete()
            return True
        except ProjectMembership.DoesNotExist:
            return False

    def is_member(self, user):
        """Check if user is a member of the project."""
        return self.users.filter(id=user.id).exists()

    def can_edit(self, user):
        """Check if user can edit the project."""
        try:
            membership = ProjectMembership.objects.get(user=user, project=self)
            return membership.can_edit_project
        except ProjectMembership.DoesNotExist:
            return False


class ProjectMembership(models.Model):
    """User membership in projects with roles and permissions."""

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="memberships"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="memberships"
    )

    # Role and Permissions
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Administrator"),
        ("researcher", "Researcher"),
        ("viewer", "Viewer"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="researcher")

    # Permissions
    can_edit_project = models.BooleanField(default=False)
    can_manage_members = models.BooleanField(default=False)
    can_upload_documents = models.BooleanField(default=True)
    can_edit_entities = models.BooleanField(default=True)
    can_export_data = models.BooleanField(default=True)

    # Membership Details
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "projects_project_membership"
        verbose_name = "Project Membership"
        verbose_name_plural = "Project Memberships"
        unique_together = ["user", "project"]
        indexes = [
            models.Index(fields=["user", "project"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"

    def save(self, *args, **kwargs):
        # Set permissions based on role
        if self.role == "owner":
            self.can_edit_project = True
            self.can_manage_members = True
            self.can_upload_documents = True
            self.can_edit_entities = True
            self.can_export_data = True
        elif self.role == "admin":
            self.can_edit_project = True
            self.can_manage_members = True
            self.can_upload_documents = True
            self.can_edit_entities = True
            self.can_export_data = True
        elif self.role == "researcher":
            self.can_edit_project = False
            self.can_manage_members = False
            self.can_upload_documents = True
            self.can_edit_entities = True
            self.can_export_data = True
        elif self.role == "viewer":
            self.can_edit_project = False
            self.can_manage_members = False
            self.can_upload_documents = False
            self.can_edit_entities = False
            self.can_export_data = False

        super().save(*args, **kwargs)

    def get_permissions_display(self):
        """Get human-readable permissions."""
        permissions = []
        if self.can_edit_project:
            permissions.append("Edit Project")
        if self.can_manage_members:
            permissions.append("Manage Members")
        if self.can_upload_documents:
            permissions.append("Upload Documents")
        if self.can_edit_entities:
            permissions.append("Edit Entities")
        if self.can_export_data:
            permissions.append("Export Data")

        return ", ".join(permissions) if permissions else "View Only"
