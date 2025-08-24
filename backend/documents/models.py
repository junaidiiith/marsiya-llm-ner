from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import UserStampedModel, SoftDeleteModel
import difflib


class Document(UserStampedModel, SoftDeleteModel):
    """Text document for NER processing and analysis."""
    
    # Basic Information
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    content = models.TextField()
    
    # File Information
    file = models.FileField(
        upload_to='documents/',
        blank=True,
        null=True,
        help_text="Original uploaded file"
    )
    
    # Document Metadata
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='documents'
    )
    
    # File Information
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    encoding = models.CharField(max_length=50, default='utf-8')
    
    # Processing Status
    PROCESSING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default='pending'
    )
    
    # Processing Details
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    processing_duration = models.DurationField(null=True, blank=True)
    
    # Text Analysis
    word_count = models.IntegerField(default=0)
    character_count = models.IntegerField(default=0)
    line_count = models.IntegerField(default=0)
    language = models.CharField(max_length=10, default='ur')
    
    # Entity Information
    total_entities = models.IntegerField(default=0)
    verified_entities = models.IntegerField(default=0)
    unverified_entities = models.IntegerField(default=0)
    
    # Quality Metrics
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    quality_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # Metadata
    tags = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'documents_document'
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['project']),
            models.Index(fields=['processing_status']),
            models.Index(fields=['language']),
            models.Index(fields=['created_by']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def clean(self):
        """Validate document data."""
        if self.word_count < 0:
            raise ValidationError("Word count cannot be negative")
        
        if self.character_count < 0:
            raise ValidationError("Character count cannot be negative")
        
        if self.line_count < 0:
            raise ValidationError("Line count cannot be negative")
        
        if self.confidence_score and (self.confidence_score < 0 or self.confidence_score > 1):
            raise ValidationError("Confidence score must be between 0 and 1")
        
        if self.quality_score and (self.quality_score < 0 or self.quality_score > 1):
            raise ValidationError("Quality score must be between 0 and 1")
    
    def save(self, *args, **kwargs):
        """Override save to calculate text metrics."""
        if self.content:
            self.calculate_text_metrics()
        super().save(*args, **kwargs)
    
    def calculate_text_metrics(self):
        """Calculate text analysis metrics."""
        lines = self.content.split('\n')
        self.line_count = len(lines)
        
        words = self.content.split()
        self.word_count = len(words)
        
        self.character_count = len(self.content)
    
    def start_processing(self):
        """Mark document as processing."""
        self.processing_status = 'processing'
        self.processing_started_at = timezone.now()
        self.save(update_fields=['processing_status', 'processing_started_at'])
    
    def complete_processing(self, success=True):
        """Mark document as completed or failed."""
        self.processing_completed_at = timezone.now()
        
        if success:
            self.processing_status = 'completed'
            if self.processing_started_at:
                self.processing_duration = self.processing_completed_at - self.processing_started_at
        else:
            self.processing_status = 'failed'
        
        self.save(update_fields=[
            'processing_status', 'processing_completed_at', 'processing_duration'
        ])
    
    def cancel_processing(self):
        """Cancel document processing."""
        self.processing_status = 'cancelled'
        self.processing_completed_at = timezone.now()
        if self.processing_started_at:
            self.processing_duration = self.processing_completed_at - self.processing_started_at
        self.save(update_fields=[
            'processing_status', 'processing_completed_at', 'processing_duration'
        ])
    
    def get_entities_by_type(self):
        """Get entities grouped by type."""
        from entities.models import Entity
        
        entities = Entity.objects.filter(
            document=self,
            is_deleted=False
        ).select_related('entity_type')
        
        grouped = {}
        for entity in entities:
            entity_type = entity.entity_type.name
            if entity_type not in grouped:
                grouped[entity_type] = []
            grouped[entity_type].append(entity)
        
        return grouped
    
    def get_entities_by_line(self):
        """Get entities grouped by line number."""
        from entities.models import Entity
        
        entities = Entity.objects.filter(
            document=self,
            is_deleted=False
        ).select_related('entity_type').order_by('line_number', 'start_position')
        
        grouped = {}
        for entity in entities:
            line_num = entity.line_number
            if line_num not in grouped:
                grouped[line_num] = []
            grouped[line_num].append(entity)
        
        return grouped
    
    def add_tag(self, tag):
        """Add tag to document."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.save(update_fields=['tags'])
    
    def remove_tag(self, tag):
        """Remove tag from document."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.save(update_fields=['tags'])
    
    def set_metadata(self, key, value):
        """Set document metadata."""
        self.metadata[key] = value
        self.save(update_fields=['metadata'])
    
    def get_metadata(self, key, default=None):
        """Get document metadata."""
        return self.metadata.get(key, default)
    
    def update_entity_counts(self):
        """Update entity count fields."""
        from entities.models import Entity
        
        total = Entity.objects.filter(document=self, is_deleted=False).count()
        verified = Entity.objects.filter(
            document=self, 
            is_deleted=False, 
            is_verified=True
        ).count()
        
        self.total_entities = total
        self.verified_entities = verified
        self.unverified_entities = total - verified
        
        self.save(update_fields=[
            'total_entities', 'verified_entities', 'unverified_entities'
        ])


class DocumentVersion(models.Model):
    """Version history for documents."""
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    
    # Version Information
    version_number = models.PositiveIntegerField()
    content = models.TextField()
    change_summary = models.TextField(blank=True)
    
    # Change Tracking
    changed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='document_versions'
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    
    # Metadata
    diff_summary = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'documents_document_version'
        verbose_name = 'Document Version'
        verbose_name_plural = 'Document Versions'
        unique_together = ['document', 'version_number']
        ordering = ['-version_number']
        indexes = [
            models.Index(fields=['document', 'version_number']),
            models.Index(fields=['changed_by']),
            models.Index(fields=['changed_at']),
        ]
    
    def __str__(self):
        return f"{self.document.title} v{self.version_number}"
    
    def get_diff_from_previous(self):
        """Get diff from previous version."""
        previous = DocumentVersion.objects.filter(
            document=self.document,
            version_number__lt=self.version_number
        ).order_by('-version_number').first()
        
        if previous:
            return difflib.unified_diff(
                previous.content.splitlines(keepends=True),
                self.content.splitlines(keepends=True),
                fromfile=f'v{previous.version_number}',
                tofile=f'v{self.version_number}'
            )
        return None
    
    def get_diff_summary(self):
        """Get human-readable diff summary."""
        if not self.diff_summary:
            return "No changes recorded"
        
        summary = []
        if 'lines_added' in self.diff_summary:
            summary.append(f"{self.diff_summary['lines_added']} lines added")
        if 'lines_removed' in self.diff_summary:
            summary.append(f"{self.diff_summary['lines_removed']} lines removed")
        if 'lines_modified' in self.diff_summary:
            summary.append(f"{self.diff_summary['lines_modified']} lines modified")
        
        return ', '.join(summary) if summary else "Content updated"
