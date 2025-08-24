from django.contrib import admin
from .models import Project, ProjectMembership


class ProjectMembershipInline(admin.TabularInline):
    """Inline admin for ProjectMembership."""
    model = ProjectMembership
    extra = 1
    fields = ('user', 'role', 'can_edit_project', 'can_manage_members', 'is_active')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin for Project model."""
    list_display = ('name', 'status', 'created_by', 'created_at', 'is_public')
    list_filter = ('status', 'is_public', 'created_at', 'research_area')
    search_fields = ('name', 'description', 'research_area')
    readonly_fields = ('created_at', 'updated_at', 'slug')
    inlines = [ProjectMembershipInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'slug', 'research_area')
        }),
        ('Project Details', {
            'fields': ('methodology', 'objectives', 'timeline')
        }),
        ('Status & Access', {
            'fields': ('status', 'is_public', 'allow_public_view')
        }),
        ('Metadata', {
            'fields': ('tags', 'references')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    """Admin for ProjectMembership model."""
    list_display = ('user', 'project', 'role', 'joined_at', 'is_active')
    list_filter = ('role', 'is_active', 'joined_at')
    search_fields = ('user__username', 'user__email', 'project__name')
    readonly_fields = ('joined_at',)
    
    fieldsets = (
        ('Membership', {
            'fields': ('user', 'project', 'role')
        }),
        ('Permissions', {
            'fields': ('can_edit_project', 'can_manage_members', 'can_upload_documents', 'can_edit_entities', 'can_export_data')
        }),
        ('Details', {
            'fields': ('is_active', 'notes', 'joined_at')
        }),
    )
