"""
Unit tests for users models.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from users.models import UserProfile

User = get_user_model()


class TestUserModel(TestCase):
    """Test User model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_user_creation(self):
        """Test user creation."""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_user_creation_without_username(self):
        """Test user creation without username."""
        user_data = self.user_data.copy()
        del user_data['username']
        
        with self.assertRaises(ValueError):
            User.objects.create_user(**user_data)
    
    def test_user_creation_without_email(self):
        """Test user creation without email."""
        user_data = self.user_data.copy()
        del user_data['email']
        
        with self.assertRaises(ValueError):
            User.objects.create_user(**user_data)
    
    def test_superuser_creation(self):
        """Test superuser creation."""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_user_str_representation(self):
        """Test string representation of user."""
        user = User.objects.create_user(**self.user_data)
        expected_str = 'testuser (test@example.com)'
        self.assertEqual(str(user), expected_str)
    
    def test_user_full_name(self):
        """Test user full name property."""
        user = User.objects.create_user(**self.user_data)
        expected_full_name = 'Test User'
        self.assertEqual(user.get_full_name(), expected_full_name)
    
    def test_user_short_name(self):
        """Test user short name property."""
        user = User.objects.create_user(**self.user_data)
        expected_short_name = 'Test'
        self.assertEqual(user.get_short_name(), expected_short_name)
    
    def test_user_email_normalization(self):
        """Test email normalization."""
        user_data = self.user_data.copy()
        user_data['email'] = 'TEST@EXAMPLE.COM'
        
        user = User.objects.create_user(**user_data)
        self.assertEqual(user.email, 'test@example.com')
    
    def test_user_unique_constraints(self):
        """Test unique constraints."""
        # Create first user
        User.objects.create_user(**self.user_data)
        
        # Try to create user with same username
        user_data2 = self.user_data.copy()
        user_data2['email'] = 'test2@example.com'
        
        with self.assertRaises(Exception):
            User.objects.create_user(**user_data2)
        
        # Try to create user with same email
        user_data3 = self.user_data.copy()
        user_data3['username'] = 'testuser2'
        
        with self.assertRaises(Exception):
            User.objects.create_user(**user_data3)
    
    def test_user_password_validation(self):
        """Test password validation."""
        user_data = self.user_data.copy()
        user_data['password'] = '123'  # Too short
        
        with self.assertRaises(ValidationError):
            user = User.objects.create_user(**user_data)
            user.full_clean()
    
    def test_user_activation(self):
        """Test user activation/deactivation."""
        user = User.objects.create_user(**self.user_data)
        
        # Deactivate user
        user.is_active = False
        user.save()
        self.assertFalse(user.is_active)
        
        # Reactivate user
        user.is_active = True
        user.save()
        self.assertTrue(user.is_active)
    
    def test_user_last_login(self):
        """Test user last login tracking."""
        user = User.objects.create_user(**self.user_data)
        
        from django.utils import timezone
        now = timezone.now()
        user.last_login = now
        user.save()
        
        user.refresh_from_db()
        self.assertEqual(user.last_login, now)


class TestUserProfileModel(TestCase):
    """Test UserProfile model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.profile_data = {
            'user': self.user,
            'research_interests': 'Digital Humanities, Urdu Literature',
            'institution': 'Test University',
            'role': 'Researcher',
            'bio': 'A researcher interested in digital humanities.',
            'website': 'https://example.com',
            'location': 'Test City, Test Country',
            'preferences': {
                'language': 'en',
                'theme': 'light',
                'notifications': True
            }
        }
    
    def test_profile_creation(self):
        """Test profile creation."""
        profile = UserProfile.objects.create(**self.profile_data)
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.research_interests, 'Digital Humanities, Urdu Literature')
        self.assertEqual(profile.institution, 'Test University')
        self.assertEqual(profile.role, 'Researcher')
        self.assertEqual(profile.bio, 'A researcher interested in digital humanities.')
        self.assertEqual(profile.website, 'https://example.com')
        self.assertEqual(profile.location, 'Test City, Test Country')
        self.assertEqual(profile.preferences['language'], 'en')
    
    def test_profile_str_representation(self):
        """Test string representation of profile."""
        profile = UserProfile.objects.create(**self.profile_data)
        expected_str = f'Profile for {self.user.username}'
        self.assertEqual(str(profile), expected_str)
    
    def test_profile_user_relationship(self):
        """Test profile user relationship."""
        profile = UserProfile.objects.create(**self.profile_data)
        
        # Test reverse relationship
        self.assertEqual(self.user.profile, profile)
        
        # Test profile can access user
        self.assertEqual(profile.user.username, 'testuser')
        self.assertEqual(profile.user.email, 'test@example.com')
    
    def test_profile_optional_fields(self):
        """Test profile optional fields."""
        minimal_profile = UserProfile.objects.create(
            user=self.user,
            research_interests='Digital Humanities'
        )
        
        self.assertIsNone(minimal_profile.institution)
        self.assertIsNone(minimal_profile.role)
        self.assertIsNone(minimal_profile.bio)
        self.assertIsNone(minimal_profile.website)
        self.assertIsNone(minimal_profile.location)
        self.assertEqual(minimal_profile.preferences, {})
    
    def test_profile_preferences_json(self):
        """Test profile preferences JSON field."""
        complex_preferences = {
            'ui': {
                'language': 'en',
                'theme': 'dark',
                'font_size': 'medium'
            },
            'notifications': {
                'email': True,
                'push': False,
                'frequency': 'daily'
            },
            'research': {
                'default_language': 'urdu',
                'auto_save': True,
                'export_format': 'json'
            }
        }
        
        profile = UserProfile.objects.create(
            user=self.user,
            research_interests='Digital Humanities',
            preferences=complex_preferences
        )
        
        # Refresh from database
        profile.refresh_from_db()
        self.assertEqual(profile.preferences, complex_preferences)
        self.assertEqual(profile.preferences['ui']['theme'], 'dark')
        self.assertEqual(profile.preferences['notifications']['email'], True)
    
    def test_profile_research_interests_validation(self):
        """Test research interests validation."""
        # Test with very long research interests
        long_interests = 'A' * 1000
        
        profile = UserProfile.objects.create(
            user=self.user,
            research_interests=long_interests
        )
        
        self.assertEqual(profile.research_interests, long_interests)
    
    def test_profile_institution_validation(self):
        """Test institution validation."""
        # Test with very long institution name
        long_institution = 'A' * 200
        
        profile = UserProfile.objects.create(
            user=self.user,
            research_interests='Digital Humanities',
            institution=long_institution
        )
        
        self.assertEqual(profile.institution, long_institution)
    
    def test_profile_role_choices(self):
        """Test profile role choices."""
        valid_roles = ['Researcher', 'Student', 'Professor', 'Librarian', 'Other']
        
        for role in valid_roles:
            profile = UserProfile.objects.create(
                user=User.objects.create_user(
                    username=f'user_{role.lower()}',
                    email=f'{role.lower()}@example.com',
                    password='testpass123'
                ),
                research_interests='Digital Humanities',
                role=role
            )
            self.assertEqual(profile.role, role)
    
    def test_profile_website_validation(self):
        """Test website URL validation."""
        valid_urls = [
            'https://example.com',
            'http://test.org',
            'https://subdomain.example.co.uk',
            'https://example.com/path?param=value'
        ]
        
        for url in valid_urls:
            profile = UserProfile.objects.create(
                user=User.objects.create_user(
                    username=f'user_{url.split("//")[1].replace(".", "_")}',
                    email=f'{url.split("//")[1].replace(".", "_")}@example.com',
                    password='testpass123'
                ),
                research_interests='Digital Humanities',
                website=url
            )
            self.assertEqual(profile.website, url)
    
    def test_profile_metadata_default(self):
        """Test profile metadata default value."""
        profile = UserProfile.objects.create(
            user=self.user,
            research_interests='Digital Humanities'
        )
        
        self.assertEqual(profile.metadata, {})
    
    def test_profile_metadata_json(self):
        """Test profile metadata JSON field."""
        metadata = {
            'publications': ['Paper 1', 'Paper 2'],
            'grants': ['Grant 1', 'Grant 2'],
            'conferences': ['Conference 1'],
            'skills': {
                'languages': ['Urdu', 'English', 'Arabic'],
                'tools': ['Python', 'Django', 'React'],
                'methodologies': ['Digital Humanities', 'Text Analysis']
            }
        }
        
        profile = UserProfile.objects.create(
            user=self.user,
            research_interests='Digital Humanities',
            metadata=metadata
        )
        
        # Refresh from database
        profile.refresh_from_db()
        self.assertEqual(profile.metadata, metadata)
        self.assertEqual(profile.metadata['skills']['languages'], ['Urdu', 'English', 'Arabic'])


class TestUserProfileIntegration(TestCase):
    """Integration tests for User and UserProfile."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_profile_creation_workflow(self):
        """Test complete user profile creation workflow."""
        # Create user profile
        profile = UserProfile.objects.create(
            user=self.user,
            research_interests='Digital Humanities, Urdu Literature',
            institution='Test University',
            role='Researcher'
        )
        
        # Verify relationships
        self.assertEqual(self.user.profile, profile)
        self.assertEqual(profile.user, self.user)
        
        # Verify profile data
        self.assertEqual(profile.research_interests, 'Digital Humanities, Urdu Literature')
        self.assertEqual(profile.institution, 'Test University')
        self.assertEqual(profile.role, 'Researcher')
    
    def test_user_profile_update_workflow(self):
        """Test user profile update workflow."""
        # Create initial profile
        profile = UserProfile.objects.create(
            user=self.user,
            research_interests='Digital Humanities',
            institution='Old University'
        )
        
        # Update profile
        profile.institution = 'New University'
        profile.role = 'Professor'
        profile.save()
        
        # Refresh from database
        profile.refresh_from_db()
        
        # Verify updates
        self.assertEqual(profile.institution, 'New University')
        self.assertEqual(profile.role, 'Professor')
    
    def test_user_profile_deletion_cascade(self):
        """Test that profile is deleted when user is deleted."""
        profile = UserProfile.objects.create(
            user=self.user,
            research_interests='Digital Humanities'
        )
        
        profile_id = profile.id
        
        # Delete user
        self.user.delete()
        
        # Verify profile is also deleted
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(id=profile_id)
    
    def test_multiple_users_with_profiles(self):
        """Test multiple users with profiles."""
        users_data = [
            {
                'username': 'user1',
                'email': 'user1@example.com',
                'research_interests': 'Digital Humanities',
                'institution': 'University 1'
            },
            {
                'username': 'user2',
                'email': 'user2@example.com',
                'research_interests': 'Urdu Literature',
                'institution': 'University 2'
            },
            {
                'username': 'user3',
                'email': 'user3@example.com',
                'research_interests': 'Islamic Studies',
                'institution': 'University 3'
            }
        ]
        
        created_profiles = []
        
        for user_data in users_data:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password='testpass123'
            )
            
            profile = UserProfile.objects.create(
                user=user,
                research_interests=user_data['research_interests'],
                institution=user_data['institution']
            )
            
            created_profiles.append(profile)
        
        # Verify all profiles were created
        self.assertEqual(len(created_profiles), 3)
        
        # Verify each profile has correct data
        for i, profile in enumerate(created_profiles):
            user_data = users_data[i]
            self.assertEqual(profile.user.username, user_data['username'])
            self.assertEqual(profile.research_interests, user_data['research_interests'])
            self.assertEqual(profile.institution, user_data['institution'])
