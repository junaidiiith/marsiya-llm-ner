from django.contrib import admin
from .models import EntityType, Entity, EntityRelationship


@admin.register(EntityType)
class EntityTypeAdmin(admin.ModelAdmin):
    """Admin for EntityType model."""
    list_display = ('name', 'display_name', 'is_active', 'is_system', 'sort_order')
    list_filter = ('is_active', 'is_system')
    search_fields = ('name', 'display_name', 'description')
    ordering = ('sort_order', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'description')
        }),
        ('Visual Representation', {
            'fields': ('color_code', 'icon')
        }),
        ('Configuration', {
            'fields': ('is_active', 'is_system', 'sort_order')
        }),
        ('Validation & Examples', {
            'fields': ('validation_rules', 'examples')
        }),
    )


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    """Admin for Entity model."""
    list_display = ('text', 'entity_type', 'document', 'line_number', 'is_verified', 'confidence_score', 'source')
    list_filter = ('entity_type', 'is_verified', 'source', 'created_at')
    search_fields = ('text', 'document__title', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Entity Information', {
            'fields': ('text', 'entity_type', 'document')
        }),
        ('Position Information', {
            'fields': ('start_position', 'end_position', 'line_number', 'word_position')
        }),
        ('Confidence & Quality', {
            'fields': ('confidence_score', 'quality_score')
        }),
        ('Verification Status', {
            'fields': ('is_verified', 'verified_by', 'verified_at', 'verification_notes')
        }),
        ('Processing Information', {
            'fields': ('source', 'context_before', 'context_after')
        }),
        ('Metadata', {
            'fields': ('tags', 'attributes', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EntityRelationship)
class EntityRelationshipAdmin(admin.ModelAdmin):
    """Admin for EntityRelationship model."""
    list_display = ('source_entity', 'relationship_type', 'target_entity', 'confidence_score', 'is_verified')
    list_filter = ('relationship_type', 'is_verified', 'created_at')
    search_fields = ('source_entity__text', 'target_entity__text')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Relationship', {
            'fields': ('source_entity', 'relationship_type', 'target_entity')
        }),
        ('Details', {
            'fields': ('confidence_score', 'is_verified', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
