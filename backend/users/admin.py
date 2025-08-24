from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    """Custom User admin."""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_researcher', 'is_admin')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_researcher', 'is_admin', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Research Profile', {
            'fields': ('bio', 'institution', 'academic_title', 'research_focus', 'research_interests')
        }),
        ('Preferences', {
            'fields': ('preferences',)
        }),
        ('System Fields', {
            'fields': ('is_researcher', 'is_admin', 'email_verified', 'last_activity')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Research Profile', {
            'fields': ('bio', 'institution', 'academic_title', 'research_focus', 'research_interests')
        }),
    )


admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
