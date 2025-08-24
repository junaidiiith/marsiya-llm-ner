# Database Schema - Urdu Marsiya NER Web Application

## Table of Contents

1. [Overview](#overview)
2. [Database Design Principles](#database-design-principles)
3. [Core Models](#core-models)
4. [User Management Models](#user-management-models)
5. [Project Management Models](#project-management-models)
6. [Document Management Models](#document-management-models)
7. [Entity Management Models](#entity-management-models)
8. [LLM Integration Models](#llm-integration-models)
9. [Processing and Jobs Models](#processing-and-jobs-models)
10. [Audit and Logging Models](#audit-and-logging-models)
11. [Database Relationships](#database-relationships)
12. [Indexes and Performance](#indexes-and-performance)
13. [Migrations Strategy](#migrations-strategy)
14. [Data Integrity](#data-integrity)

## Overview

The database schema is designed to support a comprehensive Named Entity Recognition (NER) application for Urdu Marsiya poetry. The schema follows Django ORM conventions and is optimized for:

- **Scalability**: Handle large volumes of text documents and entities
- **Performance**: Efficient querying and data retrieval
- **Data Integrity**: Maintain consistency across related data
- **Audit Trail**: Track changes and user actions
- **Collaboration**: Support multiple users working on shared projects

## Database Design Principles

### 1. Normalization

- Follow 3NF (Third Normal Form) to minimize data redundancy
- Use foreign keys for referential integrity
- Separate concerns into logical model groups

### 2. Performance Optimization

- Strategic indexing for common query patterns
- Efficient relationship design
- Pagination support for large datasets

### 3. Flexibility

- JSON fields for extensible data structures
- Configurable entity types and processing options
- Support for multiple LLM providers

### 4. Security

- User permission-based access control
- Audit logging for sensitive operations
- Secure storage of API keys and credentials

## Core Models

### Abstract Base Models

#### TimestampedModel

```python
class TimestampedModel(models.Model):
    """Abstract base model with created_at and updated_at fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

#### UserStampedModel

```python
class UserStampedModel(TimestampedModel):
    """Abstract base model with user tracking."""
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='%(class)s_updated',
        null=True,
        blank=True
    )

    class Meta:
        abstract = True
```

## User Management Models

### User Model

```python
class User(AbstractUser):
    """Extended user model with research-specific fields."""

    # Basic Information
    bio = models.TextField(blank=True, max_length=1000)
    research_interests = models.JSONField(
        default=list,
        help_text="List of research interests and specializations"
    )

    # Preferences and Settings
    preferences = models.JSONField(
        default=dict,
        help_text="User preferences including UI settings, language, etc."
    )

    # Research Profile
    institution = models.CharField(max_length=200, blank=True)
    academic_title = models.CharField(max_length=100, blank=True)
    research_focus = models.CharField(max_length=200, blank=True)

    # System Fields
    is_researcher = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    last_activity = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['last_activity']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def get_research_interests_display(self):
        return ", ".join(self.research_interests) if self.research_interests else "Not specified"

    def update_last_activity(self):
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
```

### UserProfile Model

```python
class UserProfile(models.Model):
    """Additional user profile information."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Contact Information
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    social_media = models.JSONField(default=dict)

    # Research Information
    publications = models.JSONField(default=list)
    grants = models.JSONField(default=list)
    collaborations = models.JSONField(default=list)

    # Preferences
    notification_preferences = models.JSONField(default=dict)
    privacy_settings = models.JSONField(default=dict)

    # System
    profile_completion = models.IntegerField(default=0)

    class Meta:
        db_table = 'users_user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile for {self.user.username}"

    def calculate_profile_completion(self):
        """Calculate profile completion percentage."""
        fields = ['bio', 'institution', 'research_focus', 'phone']
        completed = sum(1 for field in fields if getattr(self.user, field, ''))
        self.profile_completion = int((completed / len(fields)) * 100)
        self.save(update_fields=['profile_completion'])
```

## Project Management Models

### Project Model

```python
class Project(UserStampedModel):
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
        'users.User',
        through='ProjectMembership',
        related_name='projects'
    )

    # Project Status
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning'
    )

    # Access Control
    is_public = models.BooleanField(default=False)
    allow_public_view = models.BooleanField(default=False)

    # Metadata
    tags = models.JSONField(default=list)
    references = models.JSONField(default=list)

    class Meta:
        db_table = 'projects_project'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['is_public']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project-detail', kwargs={'slug': self.slug})

    def get_member_count(self):
        return self.users.count()

    def get_document_count(self):
        return self.documents.count()

    def get_entity_count(self):
        return Entity.objects.filter(document__project=self).count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
```

### ProjectMembership Model

```python
class ProjectMembership(models.Model):
    """User membership in projects with roles and permissions."""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='project_memberships'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    # Role and Permissions
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('researcher', 'Researcher'),
        ('viewer', 'Viewer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='researcher')

    # Permissions
    can_edit_project = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_upload_documents = models.BooleanField(default=True)
    can_edit_entities = models.BooleanField(default=True)
    can_export_data = models.BooleanField(default=True)

    # Membership Details
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'projects_project_membership'
        verbose_name = 'Project Membership'
        verbose_name_plural = 'Project Memberships'
        unique_together = ['user', 'project']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
            models.Index(fields=['joined_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"

    def save(self, *args, **kwargs):
        # Set permissions based on role
        if self.role == 'owner':
            self.can_edit_project = True
            self.can_manage_users = True
            self.can_upload_documents = True
            self.can_edit_entities = True
            self.can_export_data = True
        elif self.role == 'admin':
            self.can_edit_project = True
            self.can_manage_users = True
            self.can_upload_documents = True
            self.can_edit_entities = True
            self.can_export_data = True
        elif self.role == 'researcher':
            self.can_edit_project = False
            self.can_manage_users = False
            self.can_upload_documents = True
            self.can_edit_entities = True
            self.can_export_data = True
        elif self.role == 'viewer':
            self.can_edit_project = False
            self.can_manage_users = False
            self.can_upload_documents = False
            self.can_edit_entities = False
            self.can_export_data = False

        super().save(*args, **kwargs)
```

## Document Management Models

### Document Model

```python
class Document(UserStampedModel):
    """Text document for NER processing and analysis."""

    # Basic Information
    title = models.CharField(max_length=200, db_index=True)
    content = models.TextField()
    file_path = models.FileField(
        upload_to='documents/%Y/%m/%d/',
        null=True,
        blank=True,
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
    confidence_score = models.FloatField(null=True, blank=True)
    quality_score = models.FloatField(null=True, blank=True)

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
            models.Index(fields=['processing_status']),
            models.Index(fields=['project']),
            models.Index(fields=['created_at']),
            models.Index(fields=['language']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('document-detail', kwargs={'pk': self.pk})

    def calculate_text_metrics(self):
        """Calculate text statistics."""
        self.word_count = len(self.content.split())
        self.character_count = len(self.content)
        self.line_count = self.content.count('\n') + 1
        self.save(update_fields=['word_count', 'character_count', 'line_count'])

    def get_verification_rate(self):
        """Calculate entity verification rate."""
        if self.total_entities > 0:
            return self.verified_entities / self.total_entities
        return 0.0

    def get_processing_status_display(self):
        return dict(self.PROCESSING_STATUS_CHOICES)[self.processing_status]

    def save(self, *args, **kwargs):
        if not self.pk:  # New document
            self.calculate_text_metrics()
        super().save(*args, **kwargs)
```

### DocumentVersion Model

```python
class DocumentVersion(models.Model):
    """Version history for documents."""

    document = models.ForeignKey(
        'documents.Document',
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
        on_delete=models.CASCADE,
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

    def __str__(self):
        return f"{self.document.title} v{self.version_number}"

    def get_diff_from_previous(self):
        """Generate diff from previous version."""
        previous = self.document.versions.filter(
            version_number__lt=self.version_number
        ).order_by('-version_number').first()

        if previous:
            return difflib.unified_diff(
                previous.content.splitlines(keepends=True),
                self.content.splitlines(keepends=True),
                fromfile=f"v{previous.version_number}",
                tofile=f"v{self.version_number}"
            )
        return []
```

## Entity Management Models

### EntityType Model

```python
class EntityType(models.Model):
    """Configurable entity types for NER tagging."""

    # Basic Information
    name = models.CharField(max_length=50, unique=True, db_index=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()

    # Visual Representation
    color_code = models.CharField(
        max_length=7,
        validators=[RegexValidator(r'^#[0-9A-Fa-f]{6}$')],
        help_text="Hex color code (e.g., #87CEEB)"
    )
    icon = models.CharField(max_length=50, blank=True)

    # Configuration
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    # Validation Rules
    validation_rules = models.JSONField(default=dict)
    examples = models.JSONField(default=list)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'entities_entity_type'
        verbose_name = 'Entity Type'
        verbose_name_plural = 'Entity Types'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['sort_order']),
        ]
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.display_name

    def get_color_rgb(self):
        """Convert hex color to RGB values."""
        hex_color = self.color_code.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def get_examples_display(self):
        """Get formatted examples string."""
        return ", ".join(self.examples) if self.examples else "No examples"

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.name.title()
        super().save(*args, **kwargs)
```

### Entity Model

```python
class Entity(UserStampedModel):
    """Named entity extracted from text documents."""

    # Entity Information
    text = models.CharField(max_length=500, db_index=True)
    entity_type = models.ForeignKey(
        'entities.EntityType',
        on_delete=models.CASCADE,
        related_name='entities'
    )
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='entities'
    )

    # Position Information
    start_position = models.PositiveIntegerField()
    end_position = models.PositiveIntegerField()
    line_number = models.PositiveIntegerField()
    word_position = models.PositiveIntegerField()

    # Confidence and Quality
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    quality_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    # Verification Status
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_entities'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)

    # Processing Information
    source = models.CharField(
        max_length=50,
        choices=[
            ('llm', 'LLM Extraction'),
            ('manual', 'Manual Tagging'),
            ('import', 'Data Import'),
            ('correction', 'Manual Correction'),
        ],
        default='llm'
    )

    # Context and Relationships
    context_before = models.CharField(max_length=200, blank=True)
    context_after = models.CharField(max_length=200, blank=True)
    related_entities = models.ManyToManyField(
        'self',
        through='EntityRelationship',
        symmetrical=False,
        related_name='related_to'
    )

    # Metadata
    tags = models.JSONField(default=list)
    attributes = models.JSONField(default=dict)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'entities_entity'
        verbose_name = 'Entity'
        verbose_name_plural = 'Entities'
        indexes = [
            models.Index(fields=['text']),
            models.Index(fields=['entity_type']),
            models.Index(fields=['document']),
            models.Index(fields=['start_position']),
            models.Index(fields=['end_position']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['source']),
        ]
        ordering = ['document', 'start_position']

    def __str__(self):
        return f"{self.text} ({self.entity_type.name})"

    def get_absolute_url(self):
        return reverse('entity-detail', kwargs={'pk': self.pk})

    def get_context_text(self):
        """Get surrounding context text."""
        doc_content = self.document.content
        start = max(0, self.start_position - 50)
        end = min(len(doc_content), self.end_position + 50)
        return doc_content[start:end]

    def verify(self, user, notes=""):
        """Mark entity as verified."""
        self.is_verified = True
        self.verified_by = user
        self.verified_at = timezone.now()
        self.verification_notes = notes
        self.save(update_fields=[
            'is_verified', 'verified_by', 'verified_at', 'verification_notes'
        ])

    def unverify(self):
        """Mark entity as unverified."""
        self.is_verified = False
        self.verified_by = None
        self.verified_at = None
        self.verification_notes = ""
        self.save(update_fields=[
            'is_verified', 'verified_by', 'verified_at', 'verification_notes'
        ])

    def clean(self):
        """Validate entity data."""
        if self.start_position >= self.end_position:
            raise ValidationError("Start position must be less than end position")

        if self.confidence_score < 0 or self.confidence_score > 1:
            raise ValidationError("Confidence score must be between 0 and 1")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
```

### EntityRelationship Model

```python
class EntityRelationship(models.Model):
    """Relationships between entities."""

    source_entity = models.ForeignKey(
        'entities.Entity',
        on_delete=models.CASCADE,
        related_name='relationships_from'
    )
    target_entity = models.ForeignKey(
        'entities.Entity',
        on_delete=models.CASCADE,
        related_name='relationships_to'
    )

    # Relationship Information
    RELATIONSHIP_TYPES = [
        ('same_as', 'Same As'),
        ('part_of', 'Part Of'),
        ('located_in', 'Located In'),
        ('born_in', 'Born In'),
        ('died_in', 'Died In'),
        ('fought_in', 'Fought In'),
        ('related_to', 'Related To'),
        ('mentions', 'Mentions'),
        ('references', 'References'),
    ]
    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_TYPES
    )

    # Relationship Details
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    is_verified = models.BooleanField(default=False)

    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'entities_entity_relationship'
        verbose_name = 'Entity Relationship'
        verbose_name_plural = 'Entity Relationships'
        unique_together = ['source_entity', 'target_entity', 'relationship_type']
        indexes = [
            models.Index(fields=['relationship_type']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['confidence_score']),
        ]

    def __str__(self):
        return f"{self.source_entity.text} {self.get_relationship_type_display()} {self.target_entity.text}"
```

## LLM Integration Models

### LLMModel Model

```python
class LLMModel(UserStampedModel):
    """Configuration for different LLM providers and models."""

    # Basic Information
    name = models.CharField(max_length=100, db_index=True)
    provider = models.CharField(
        max_length=50,
        choices=[
            ('openai', 'OpenAI'),
            ('anthropic', 'Anthropic'),
            ('local', 'Local Model'),
            ('azure', 'Azure OpenAI'),
            ('google', 'Google AI'),
        ]
    )

    # Model Configuration
    model_name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=500)
    api_base_url = models.URLField(blank=True)

    # Provider-specific Settings
    settings = models.JSONField(default=dict)

    # Status and Configuration
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    priority = models.PositiveIntegerField(default=0)

    # Performance Metrics
    total_requests = models.PositiveIntegerField(default=0)
    successful_requests = models.PositiveIntegerField(default=0)
    failed_requests = models.PositiveIntegerField(default=0)
    average_response_time = models.FloatField(null=True, blank=True)

    # Rate Limiting
    rate_limit_per_hour = models.PositiveIntegerField(default=1000)
    rate_limit_per_minute = models.PositiveIntegerField(default=60)

    # Cost Tracking
    cost_per_1k_tokens = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    # Metadata
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list)

    class Meta:
        db_table = 'llm_integration_llm_model'
        verbose_name = 'LLM Model'
        verbose_name_plural = 'LLM Models'
        indexes = [
            models.Index(fields=['provider']),
            models.Index(fields=['is_active']),
            models.Index(fields=['priority']),
            models.Index(fields=['is_default']),
        ]
        ordering = ['priority', 'name']

    def __str__(self):
        return f"{self.name} ({self.provider})"

    def get_success_rate(self):
        """Calculate success rate percentage."""
        if self.total_requests > 0:
            return (self.successful_requests / self.total_requests) * 100
        return 0.0

    def increment_requests(self, success=True, response_time=None):
        """Increment request counters."""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

        if response_time:
            if self.average_response_time:
                self.average_response_time = (
                    (self.average_response_time + response_time) / 2
                )
            else:
                self.average_response_time = response_time

        self.save(update_fields=[
            'total_requests', 'successful_requests', 'failed_requests',
            'average_response_time'
        ])

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default model per provider
            LLMModel.objects.filter(
                provider=self.provider,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
```

### LLMProcessingConfig Model

```python
class LLMProcessingConfig(models.Model):
    """Configuration for LLM text processing."""

    llm_model = models.ForeignKey(
        'llm_integration.LLMModel',
        on_delete=models.CASCADE,
        related_name='processing_configs'
    )

    # Text Processing Settings
    chunk_size = models.PositiveIntegerField(default=1000)
    overlap_size = models.PositiveIntegerField(default=100)
    max_tokens = models.PositiveIntegerField(default=4000)

    # Entity Extraction Settings
    confidence_threshold = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    entity_types = models.ManyToManyField(
        'entities.EntityType',
        blank=True,
        related_name='llm_configs'
    )

    # Prompt Configuration
    system_prompt = models.TextField()
    user_prompt_template = models.TextField()
    examples = models.JSONField(default=list)

    # Processing Options
    enable_post_processing = models.BooleanField(default=True)
    enable_entity_validation = models.BooleanField(default=True)
    enable_confidence_scoring = models.BooleanField(default=True)

    # Metadata
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'llm_integration_llm_processing_config'
        verbose_name = 'LLM Processing Configuration'
        verbose_name_plural = 'LLM Processing Configurations'
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['llm_model']),
        ]

    def __str__(self):
        return f"{self.name} - {self.llm_model.name}"
```

## Processing and Jobs Models

### ProcessingJob Model

```python
class ProcessingJob(UserStampedModel):
    """Background job for document processing."""

    # Job Information
    job_id = models.CharField(max_length=100, unique=True, db_index=True)
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='processing_jobs'
    )
    llm_model = models.ForeignKey(
        'llm_integration.LLMModel',
        on_delete=models.CASCADE,
        related_name='processing_jobs'
    )
    processing_config = models.ForeignKey(
        'llm_integration.LLMProcessingConfig',
        on_delete=models.CASCADE,
        related_name='processing_jobs',
        null=True,
        blank=True
    )

    # Job Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('paused', 'Paused'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Progress Tracking
    progress = models.PositiveIntegerField(default=0)
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
    tokens_used = models.PositiveIntegerField(null=True, blank=True)
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True
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
        indexes = [
            models.Index(fields=['job_id']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['created_at']),
            models.Index(fields=['document']),
        ]
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"Job {self.job_id} - {self.document.title}"

    def get_absolute_url(self):
        return reverse('processing-job-detail', kwargs={'pk': self.pk})

    def start_processing(self):
        """Mark job as started."""
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def complete_job(self, result=None, error_message=None):
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

        self.save(update_fields=[
            'status', 'completed_at', 'error_message', 'result',
            'processing_time'
        ])

    def update_progress(self, progress, current_step=""):
        """Update job progress."""
        self.progress = progress
        if current_step:
            self.current_step = current_step
        self.save(update_fields=['progress', 'current_step'])

    def can_retry(self):
        """Check if job can be retried."""
        return self.retry_count < self.max_retries and self.status in ['failed', 'cancelled']

    def retry_job(self):
        """Retry failed job."""
        if self.can_retry():
            self.retry_count += 1
            self.status = 'pending'
            self.error_message = ""
            self.error_details = None
            self.save(update_fields=[
                'retry_count', 'status', 'error_message', 'error_details'
            ])
            return True
        return False
```

## Audit and Logging Models

### AuditLog Model

```python
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
        ('process', 'Process'),
        ('verify', 'Verify'),
        ('login', 'Login'),
        ('logout', 'Logout'),
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
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['resource_type']),
            models.Index(fields=['project']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} {self.resource_type} by {self.user} at {self.timestamp}"

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
```

## Database Relationships

### Entity Relationship Diagram

```
User (1) ←→ (N) ProjectMembership (N) ←→ (1) Project
Project (1) ←→ (N) Document
Document (1) ←→ (N) Entity
Entity (N) ←→ (1) EntityType
Entity (N) ←→ (N) Entity (through EntityRelationship)
Document (1) ←→ (N) ProcessingJob
ProcessingJob (N) ←→ (1) LLMModel
LLMModel (1) ←→ (N) LLMProcessingConfig
User (1) ←→ (N) AuditLog
```

### Key Relationships

1. **User ↔ Project**: Many-to-Many through ProjectMembership
2. **Project → Document**: One-to-Many
3. **Document → Entity**: One-to-Many
4. **Entity → EntityType**: Many-to-One
5. **Entity ↔ Entity**: Many-to-Many through EntityRelationship
6. **Document → ProcessingJob**: One-to-Many
7. **LLMModel → ProcessingJob**: One-to-Many

## Indexes and Performance

### Primary Indexes

```python
# User model
models.Index(fields=['username']),
models.Index(fields=['email']),
models.Index(fields=['is_active']),
models.Index(fields=['last_activity']),

# Project model
models.Index(fields=['status']),
models.Index(fields=['is_public']),
models.Index(fields=['created_at']),

# Document model
models.Index(fields=['title']),
models.Index(fields=['processing_status']),
models.Index(fields=['project']),
models.Index(fields=['created_at']),
models.Index(fields=['language']),

# Entity model
models.Index(fields=['text']),
models.Index(fields=['entity_type']),
models.Index(fields=['document']),
models.Index(fields=['start_position']),
models.Index(fields=['end_position']),
models.Index(fields=['is_verified']),
models.Index(fields=['confidence_score']),
models.Index(fields=['source']),

# ProcessingJob model
models.Index(fields=['job_id']),
models.Index(fields=['status']),
models.Index(fields=['priority']),
models.Index(fields=['created_at']),
models.Index(fields=['document']),
```

### Composite Indexes

```python
# For efficient entity queries
models.Index(fields=['document', 'start_position']),
models.Index(fields=['document', 'entity_type']),
models.Index(fields=['document', 'is_verified']),

# For efficient processing job queries
models.Index(fields=['status', 'priority']),
models.Index(fields=['document', 'status']),

# For efficient project queries
models.Index(fields=['status', 'created_at']),
models.Index(fields=['is_public', 'status']),
```

## Migrations Strategy

### Migration Guidelines

1. **Backward Compatibility**: Ensure migrations don't break existing functionality
2. **Data Preservation**: Handle data migration carefully for schema changes
3. **Rollback Plan**: Provide rollback mechanisms for failed migrations
4. **Testing**: Test migrations on staging environment before production

### Migration Types

1. **Schema Changes**: Add/remove/modify fields and tables
2. **Data Migrations**: Transform existing data to new format
3. **Index Changes**: Add/remove database indexes
4. **Constraint Changes**: Modify database constraints

## Data Integrity

### Constraints

1. **Foreign Key Constraints**: Ensure referential integrity
2. **Unique Constraints**: Prevent duplicate data
3. **Check Constraints**: Validate data ranges and formats
4. **Not Null Constraints**: Ensure required fields have values

### Validation

1. **Model Validation**: Django model field validators
2. **Custom Validation**: Business logic validation in models
3. **Form Validation**: User input validation
4. **API Validation**: Request data validation

### Data Consistency

1. **Transaction Management**: Ensure atomic operations
2. **Signal Handlers**: Maintain data consistency across models
3. **Periodic Cleanup**: Remove orphaned or invalid data
4. **Data Verification**: Regular data integrity checks
