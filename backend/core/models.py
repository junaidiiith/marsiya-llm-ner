from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import threading


class TimestampedModel(models.Model):
    """Abstract base model with timestamp fields."""
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        abstract = True


class UserStampedModel(TimestampedModel):
    """Abstract base model with user stamping."""
    
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        help_text="User who created this record"
    )
    updated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        help_text="User who last updated this record"
    )
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        # Auto-set created_by if not set
        if not self.pk and not self.created_by:
            from django.contrib.auth.models import AnonymousUser
            request = getattr(threading.current_thread(), '_request', None)
            if request and hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
                self.created_by = request.user
        
        super().save(*args, **kwargs)


class SoftDeleteModel(models.Model):
    """Abstract base model with soft delete functionality."""
    
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted',
        help_text="User who deleted this record"
    )
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete the record."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])
    
    def hard_delete(self, using=None, keep_parents=False):
        """Actually delete the record from database."""
        super().delete(using, keep_parents)
    
    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])


class AuditLog(models.Model):
    """Audit trail for system activities."""
    
    # Log Information
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    # Action Details
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('process', 'Process'),
        ('verify', 'Verify'),
    ]
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    # Resource Information
    resource_type = models.CharField(max_length=100)
    resource_id = models.PositiveIntegerField(null=True, blank=True)
    resource_name = models.CharField(max_length=200, blank=True)
    
    # Change Details
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Context
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    session_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'audit_audit_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'user']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} on {self.resource_type} by {self.user} at {self.timestamp}"
    
    @classmethod
    def log_action(cls, user, action, resource_type, resource_id=None, 
                   resource_name=None, changes=None, project=None, 
                   ip_address=None, user_agent=None, session_id=None):
        """Create audit log entry."""
        return cls.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            changes=changes or {},
            project=project,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )
