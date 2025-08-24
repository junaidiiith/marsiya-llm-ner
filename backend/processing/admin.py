from django.contrib import admin
from .models import ProcessingJob


@admin.register(ProcessingJob)
class ProcessingJobAdmin(admin.ModelAdmin):
    """Admin for ProcessingJob."""
    list_display = ('name', 'job_type', 'status', 'progress', 'created_by', 'created_at', 'processing_time')
    list_filter = ('job_type', 'status', 'priority', 'created_at')
    search_fields = ('name', 'description', 'job_id', 'created_by__username')
    readonly_fields = ('job_id', 'created_at', 'updated_at', 'started_at', 'completed_at', 'processing_time')
    ordering = ('-priority', '-created_at')
    
    fieldsets = (
        ('Job Information', {
            'fields': ('job_id', 'name', 'description', 'job_type')
        }),
        ('Target Resources', {
            'fields': ('document', 'project')
        }),
        ('Status & Progress', {
            'fields': ('status', 'progress', 'total_steps', 'current_step')
        }),
        ('Timing Information', {
            'fields': ('started_at', 'completed_at', 'estimated_completion', 'processing_time')
        }),
        ('Results & Errors', {
            'fields': ('result', 'error_message', 'error_details')
        }),
        ('Performance Metrics', {
            'fields': ('memory_usage', 'cpu_usage'),
            'classes': ('collapse',)
        }),
        ('Job Configuration', {
            'fields': ('priority', 'retry_count', 'max_retries')
        }),
        ('Metadata', {
            'fields': ('tags', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['reset_jobs', 'cancel_jobs']
    
    def reset_jobs(self, request, queryset):
        """Reset selected jobs to pending state."""
        count = 0
        for job in queryset:
            if job.can_cancel():
                job.reset()
                count += 1
        self.message_user(request, f'{count} jobs have been reset.')
    reset_jobs.short_description = "Reset selected jobs"
    
    def cancel_jobs(self, request, queryset):
        """Cancel selected jobs."""
        count = 0
        for job in queryset:
            if job.can_cancel():
                job.cancel()
                count += 1
        self.message_user(request, f'{count} jobs have been cancelled.')
    cancel_jobs.short_description = "Cancel selected jobs"
