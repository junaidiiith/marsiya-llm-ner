from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin for AuditLog."""
    list_display = ('timestamp', 'user', 'action', 'resource_type', 'resource_id', 'resource_name')
    list_filter = ('action', 'resource_type', 'timestamp', 'user')
    search_fields = ('user__username', 'user__email', 'resource_name', 'action')
    readonly_fields = ('timestamp', 'user', 'action', 'resource_type', 'resource_id', 'resource_name', 'changes', 'ip_address', 'user_agent')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Log Information', {
            'fields': ('timestamp', 'user')
        }),
        ('Action Details', {
            'fields': ('action', 'resource_type', 'resource_id', 'resource_name')
        }),
        ('Change Details', {
            'fields': ('changes',)
        }),
        ('Context Information', {
            'fields': ('ip_address', 'user_agent', 'project', 'session_id')
        }),
    )
    
    def has_add_permission(self, request):
        """Audit logs should not be manually created."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Audit logs should not be modified."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Audit logs should not be deleted."""
        return False
