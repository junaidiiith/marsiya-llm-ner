from django.contrib import admin
from .models import Document, DocumentVersion


class DocumentVersionInline(admin.TabularInline):
    """Inline admin for DocumentVersion."""
    model = DocumentVersion
    extra = 0
    readonly_fields = ('changed_at', 'changed_by')
    fields = ('version_number', 'change_summary', 'changed_by', 'changed_at')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin for Document model."""
    list_display = ('title', 'project', 'processing_status', 'language', 'total_entities', 'verified_entities', 'created_by', 'created_at')
    list_filter = ('processing_status', 'language', 'created_at', 'project')
    search_fields = ('title', 'description', 'content', 'project__name')
    readonly_fields = ('created_at', 'updated_at', 'word_count', 'character_count', 'line_count')
    inlines = [DocumentVersionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'content', 'project')
        }),
        ('File Information', {
            'fields': ('file', 'file_name', 'file_size', 'content_type', 'encoding')
        }),
        ('Processing Status', {
            'fields': ('processing_status', 'processing_started_at', 'processing_completed_at', 'processing_duration')
        }),
        ('Text Analysis', {
            'fields': ('word_count', 'character_count', 'line_count', 'language')
        }),
        ('Entity Information', {
            'fields': ('total_entities', 'verified_entities', 'unverified_entities')
        }),
        ('Quality Metrics', {
            'fields': ('confidence_score', 'quality_score')
        }),
        ('Metadata', {
            'fields': ('tags', 'metadata', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    """Admin for DocumentVersion model."""
    list_display = ('document', 'version_number', 'changed_by', 'changed_at')
    list_filter = ('version_number', 'changed_at')
    search_fields = ('document__title', 'change_summary')
    readonly_fields = ('changed_at',)
    
    fieldsets = (
        ('Version Information', {
            'fields': ('document', 'version_number', 'content')
        }),
        ('Change Details', {
            'fields': ('change_summary', 'diff_summary')
        }),
        ('Change Tracking', {
            'fields': ('changed_by', 'changed_at')
        }),
    )
