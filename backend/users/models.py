from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from core.models import TimestampedModel


class User(AbstractUser):
    """Extended user model with research-specific fields."""
    
    # Basic Information
    bio = models.TextField(blank=True, max_length=1000)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    
    # Research Profile
    institution = models.CharField(max_length=200, blank=True)
    academic_title = models.CharField(max_length=100, blank=True)
    research_focus = models.CharField(max_length=200, blank=True)
    research_interests = models.JSONField(
        default=list,
        help_text="List of research interests and specializations"
    )
    
    # Preferences and Settings
    preferences = models.JSONField(
        default=dict,
        help_text="User preferences including UI settings, language, etc."
    )
    
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
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['is_researcher']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def get_full_name(self):
        """Get user's full name or username if no name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def update_last_activity(self):
        """Update last activity timestamp."""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def get_research_interests_display(self):
        """Get formatted research interests."""
        return ', '.join(self.research_interests) if self.research_interests else 'Not specified'
    
    def get_preference(self, key, default=None):
        """Get user preference value."""
        return self.preferences.get(key, default)
    
    def set_preference(self, key, value):
        """Set user preference value."""
        self.preferences[key] = value
        self.save(update_fields=['preferences'])


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
    profile_completion = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    class Meta:
        db_table = 'users_user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"Profile for {self.user.username}"
    
    def calculate_profile_completion(self):
        """Calculate profile completion percentage."""
        fields = [
            self.user.first_name, self.user.last_name, self.user.bio,
            self.user.institution, self.user.academic_title,
            self.phone, self.website
        ]
        
        completed_fields = sum(1 for field in fields if field)
        total_fields = len(fields)
        
        self.profile_completion = int((completed_fields / total_fields) * 100)
        self.save(update_fields=['profile_completion'])
    
    def get_social_media_links(self):
        """Get formatted social media links."""
        return self.social_media
    
    def add_publication(self, publication_data):
        """Add publication to user's list."""
        if 'id' not in publication_data:
            publication_data['id'] = len(self.publications) + 1
        self.publications.append(publication_data)
        self.save(update_fields=['publications'])
    
    def add_grant(self, grant_data):
        """Add grant to user's list."""
        if 'id' not in grant_data:
            grant_data['id'] = len(self.grants) + 1
        self.grants.append(grant_data)
        self.save(update_fields=['grants'])
