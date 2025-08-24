from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import UserStampedModel, SoftDeleteModel


class EntityType(models.Model):
    """Configurable entity types for NER tagging."""
    
    # Basic Information
    name = models.CharField(max_length=50, unique=True, db_index=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Visual Representation
    color_code = models.CharField(
        max_length=7,
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
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['sort_order']),
        ]
    
    def __str__(self):
        return self.display_name
    
    def get_examples_display(self):
        """Get formatted examples."""
        return ', '.join(self.examples) if self.examples else 'No examples'
    
    def get_validation_rules_display(self):
        """Get formatted validation rules."""
        rules = []
        for key, value in self.validation_rules.items():
            rules.append(f"{key}: {value}")
        return '; '.join(rules) if rules else 'No validation rules'
    
    def get_entities_count(self):
        """Get total count of entities of this type."""
        return self.entities.count()
    
    def get_verified_entities_count(self):
        """Get count of verified entities of this type."""
        return self.entities.filter(is_verified=True).count()


class Entity(UserStampedModel, SoftDeleteModel):
    """Named entity extracted from text documents."""
    
    # Entity Information
    text = models.CharField(max_length=500, db_index=True)
    entity_type = models.ForeignKey(
        EntityType,
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
        max_length=20,
        choices=[
            ('llm', 'LLM'),
            ('manual', 'Manual'),
            ('import', 'Import'),
            ('correction', 'Correction'),
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
            models.Index(fields=['start_position', 'end_position']),
            models.Index(fields=['line_number']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['source']),
        ]
    
    def __str__(self):
        return f"{self.text} ({self.entity_type.name})"
    
    def clean(self):
        """Validate entity data."""
        if self.start_position >= self.end_position:
            raise ValidationError("Start position must be less than end position")
        
        if self.confidence_score < 0 or self.confidence_score > 1:
            raise ValidationError("Confidence score must be between 0 and 1")
        
        if self.quality_score and (self.quality_score < 0 or self.quality_score > 1):
            raise ValidationError("Quality score must be between 0 and 1")
    
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
    
    def get_context(self, document_content, context_size=50):
        """Get text context around the entity."""
        start = max(0, self.start_position - context_size)
        end = min(len(document_content), self.end_position + context_size)
        
        context_before = document_content[start:self.start_position]
        context_after = document_content[self.end_position:end]
        
        return context_before, context_after
    
    def add_tag(self, tag):
        """Add tag to entity."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.save(update_fields=['tags'])
    
    def remove_tag(self, tag):
        """Remove tag from entity."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.save(update_fields=['tags'])
    
    def set_attribute(self, key, value):
        """Set entity attribute."""
        self.attributes[key] = value
        self.save(update_fields=['attributes'])
    
    def get_attribute(self, key, default=None):
        """Get entity attribute."""
        return self.attributes.get(key, default)


class EntityRelationship(models.Model):
    """Relationships between entities."""
    
    source_entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='relationships_from'
    )
    target_entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='relationships_to'
    )
    
    # Relationship Information
    RELATIONSHIP_TYPES = [
        ('same_as', 'Same As'),
        ('part_of', 'Part Of'),
        ('contains', 'Contains'),
        ('located_in', 'Located In'),
        ('works_for', 'Works For'),
        ('married_to', 'Married To'),
        ('parent_of', 'Parent Of'),
        ('child_of', 'Child Of'),
        ('sibling_of', 'Sibling Of'),
        ('mentions', 'Mentions'),
        ('references', 'References'),
        ('custom', 'Custom'),
    ]
    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_TYPES,
        default='custom'
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
            models.Index(fields=['source_entity', 'target_entity']),
            models.Index(fields=['relationship_type']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.source_entity} --{self.relationship_type}--> {self.target_entity}"
    
    def clean(self):
        """Validate relationship data."""
        if self.source_entity == self.target_entity:
            raise ValidationError("Source and target entities cannot be the same")
        
        if self.confidence_score < 0 or self.confidence_score > 1:
            raise ValidationError("Confidence score must be between 0 and 1")
