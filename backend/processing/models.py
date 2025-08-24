from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from core.models import UserStampedModel, SoftDeleteModel
import uuid
from django.core.exceptions import ValidationError


class ProcessingJob(UserStampedModel, SoftDeleteModel):
    """Background job for document processing."""
    
    # Job Information
    job_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Job Type and Target
    JOB_TYPE_CHOICES = [
        ('ner_processing', 'NER Processing'),
        ('entity_verification', 'Entity Verification'),
        ('document_analysis', 'Document Analysis'),
        ('export_generation', 'Export Generation'),
        ('email_sending', 'Email Sending'),
        ('data_import', 'Data Import'),
        ('cleanup', 'Cleanup'),
        ('custom', 'Custom'),
    ]
    job_type = models.CharField(max_length=30, choices=JOB_TYPE_CHOICES)
    
    # Target Resources
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='processing_jobs'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='processing_jobs'
    )
    
    # Job Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('retrying', 'Retrying'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Progress Tracking
    progress = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    total_steps = models.PositiveIntegerField(default=0)
    current_step = models.CharField(max_length=200, blank=True)
    
    # Timing Information
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    
    # Results and Errors
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(null=True, blank=True)
    
    # Performance Metrics
    processing_time = models.DurationField(null=True, blank=True)
    memory_usage = models.PositiveIntegerField(null=True, blank=True)
    cpu_usage = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    
    # Job Configuration
    priority = models.PositiveIntegerField(default=0)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    
    # Metadata
    tags = models.JSONField(default=list)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'processing_processing_job'
        verbose_name = 'Processing Job'
        verbose_name_plural = 'Processing Jobs'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['job_id']),
            models.Index(fields=['job_type']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['created_by']),
            models.Index(fields=['created_at']),
            models.Index(fields=['document']),
            models.Index(fields=['project']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.job_id})"
    
    def save(self, *args, **kwargs):
        """Override save to generate job_id if not provided."""
        if not self.job_id:
            self.job_id = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate job data."""
        if self.progress < 0 or self.progress > 100:
            raise ValidationError("Progress must be between 0 and 100")
        
        if self.retry_count > self.max_retries:
            raise ValidationError("Retry count cannot exceed max retries")
        
        if self.cpu_usage and (self.cpu_usage < 0 or self.cpu_usage > 100):
            raise ValidationError("CPU usage must be between 0 and 100")
    
    def start(self):
        """Start the job."""
        self.status = 'running'
        self.started_at = timezone.now()
        self.progress = 0
        self.save(update_fields=['status', 'started_at', 'progress'])
    
    def update_progress(self, progress: int, step: str = ""):
        """Update job progress."""
        self.progress = max(0, min(100, progress))
        if step:
            self.current_step = step
        self.save(update_fields=['progress', 'current_step'])
    
    def complete(self, result=None, error_message=None):
        """Mark job as completed or failed."""
        self.completed_at = timezone.now()
        
        if error_message:
            self.status = 'failed'
            self.error_message = error_message
        else:
            self.status = 'completed'
            self.result = result
        
        if self.started_at:
            self.processing_time = self.completed_at - self.started_at
        
        self.progress = 100
        self.save(update_fields=[
            'status', 'completed_at', 'error_message', 'result',
            'processing_time', 'progress'
        ])
    
    def cancel(self):
        """Cancel the job."""
        self.status = 'cancelled'
        self.completed_at = timezone.now()
        if self.started_at:
            self.processing_time = self.completed_at - self.started_at
        self.save(update_fields=['status', 'completed_at', 'processing_time'])
    
    def retry(self):
        """Retry the job."""
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            self.status = 'retrying'
            self.error_message = ""
            self.error_details = {}
            self.save(update_fields=[
                'retry_count', 'status', 'error_message', 'error_details'
            ])
            return True
        return False
    
    def reset(self):
        """Reset job to pending state."""
        self.status = 'pending'
        self.progress = 0
        self.current_step = ""
        self.started_at = None
        self.completed_at = None
        self.processing_time = None
        self.result = None
        self.error_message = ""
        self.error_details = {}
        self.retry_count = 0
        self.save(update_fields=[
            'status', 'progress', 'current_step', 'started_at',
            'completed_at', 'processing_time', 'result', 'error_message',
            'error_details', 'retry_count'
        ])
    
    def get_processing_time_display(self):
        """Get formatted processing time."""
        if self.processing_time:
            total_seconds = int(self.processing_time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        return "Not started"
    
    def get_status_display_with_progress(self):
        """Get status with progress information."""
        if self.status == 'running':
            return f"{self.status.title()} ({self.progress}%)"
        return self.get_status_display()
    
    def is_completed(self):
        """Check if job is completed."""
        return self.status in ['completed', 'failed', 'cancelled']
    
    def is_running(self):
        """Check if job is running."""
        return self.status in ['running', 'retrying']
    
    def can_retry(self):
        """Check if job can be retried."""
        return self.status == 'failed' and self.retry_count < self.max_retries
    
    def can_cancel(self):
        """Check if job can be cancelled."""
        return self.status in ['pending', 'queued', 'running', 'retrying']
    
    def add_tag(self, tag):
        """Add tag to job."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.save(update_fields=['tags'])
    
    def remove_tag(self, tag):
        """Remove tag from job."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.save(update_fields=['tags'])
    
    def set_result(self, key, value):
        """Set result value."""
        if not self.result:
            self.result = {}
        self.result[key] = value
        self.save(update_fields=['result'])
    
    def get_result(self, key, default=None):
        """Get result value."""
        if not self.result:
            return default
        return self.result.get(key, default)
