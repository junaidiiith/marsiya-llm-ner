from django.contrib import admin
from .models import LLMModel, LLMProcessingConfig


@admin.register(LLMModel)
class LLMModelAdmin(admin.ModelAdmin):
    """Admin for LLMModel."""
    list_display = ('name', 'provider', 'model_name', 'is_active', 'is_default', 'priority', 'total_requests', 'successful_requests')
    list_filter = ('provider', 'is_active', 'is_default', 'created_at')
    search_fields = ('name', 'description', 'model_name')
    ordering = ('priority', 'name')
    readonly_fields = ('total_requests', 'successful_requests', 'failed_requests', 'average_response_time', 'total_cost')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'provider')
        }),
        ('Model Configuration', {
            'fields': ('model_name', 'api_key', 'api_base_url')
        }),
        ('Provider Settings', {
            'fields': ('settings',)
        }),
        ('Status & Priority', {
            'fields': ('is_active', 'is_default', 'priority')
        }),
        ('Performance Metrics', {
            'fields': ('total_requests', 'successful_requests', 'failed_requests', 'average_response_time'),
            'classes': ('collapse',)
        }),
        ('Rate Limiting', {
            'fields': ('rate_limit_per_hour', 'rate_limit_per_minute')
        }),
        ('Cost Tracking', {
            'fields': ('cost_per_1k_tokens', 'total_cost'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('tags',)
        }),
    )


@admin.register(LLMProcessingConfig)
class LLMProcessingConfigAdmin(admin.ModelAdmin):
    """Admin for LLMProcessingConfig."""
    list_display = ('name', 'llm_model', 'prompt_type', 'chunk_size', 'confidence_threshold', 'is_active')
    list_filter = ('prompt_type', 'is_active', 'llm_model__provider')
    search_fields = ('name', 'description', 'llm_model__name')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'llm_model', 'is_active')
        }),
        ('Text Processing Settings', {
            'fields': ('chunk_size', 'overlap_size', 'max_tokens')
        }),
        ('Entity Extraction Settings', {
            'fields': ('confidence_threshold', 'entity_types')
        }),
        ('Prompt Configuration', {
            'fields': ('prompt_type', 'custom_prompt', 'custom_entity_types', 'custom_instructions')
        }),
        ('Processing Options', {
            'fields': ('enable_post_processing', 'enable_entity_validation', 'enable_confidence_scoring')
        }),
    )
