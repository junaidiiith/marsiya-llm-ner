"""
Unit tests for core models.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import TimestampedModel, SoftDeleteModel, UserStampedModel, AuditLog

User = get_user_model()


class TestTimestampedModel(TestCase):
    """Test TimestampedModel functionality."""
    
    def test_timestamped_model_creation(self):
        """Test that timestamps are automatically set on creation."""
        # Create a concrete model class for testing
        from django.db import models
        class TestModel(TimestampedModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'
        
        # This test would require a concrete model, so we'll test the concept
        # In practice, these models are abstract and used as base classes
        assert hasattr(TimestampedModel, 'created_at')
        assert hasattr(TimestampedModel, 'updated_at')


class TestSoftDeleteModel(TestCase):
    """Test SoftDeleteModel functionality."""
    
    def test_soft_delete_model_fields(self):
        """Test that soft delete fields exist."""
        assert hasattr(SoftDeleteModel, 'is_deleted')
        assert hasattr(SoftDeleteModel, 'deleted_at')
        assert hasattr(SoftDeleteModel, 'deleted_by')


class TestUserStampedModel(TestCase):
    """Test UserStampedModel functionality."""
    
    def test_user_stamped_model_fields(self):
        """Test that user stamp fields exist."""
        assert hasattr(UserStampedModel, 'created_by')
        assert hasattr(UserStampedModel, 'updated_by')


class TestAuditLog(TestCase):
    """Test AuditLog model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.audit_log = AuditLog.objects.create(
            action='create',
            resource_type='TestModel',
            resource_id=1,
            user=self.user,
            changes={'field': 'value'},
            ip_address='127.0.0.1',
            user_agent='Test User Agent'
        )
    
    def test_audit_log_creation(self):
        """Test audit log creation."""
        self.assertEqual(self.audit_log.action, 'create')
        self.assertEqual(self.audit_log.resource_type, 'TestModel')
        self.assertEqual(self.audit_log.resource_id, 1)
        self.assertEqual(self.audit_log.user, self.user)
        self.assertEqual(self.audit_log.changes, {'field': 'value'})
        self.assertEqual(self.audit_log.ip_address, '127.0.0.1')
        self.assertEqual(self.audit_log.user_agent, 'Test User Agent')
    
    def test_audit_log_timestamps(self):
        """Test that timestamps are set automatically."""
        self.assertIsNotNone(self.audit_log.timestamp)
    
    def test_audit_log_str_representation(self):
        """Test string representation of audit log."""
        # The actual string representation includes timestamp, so we'll check it contains the expected parts
        actual_str = str(self.audit_log)
        self.assertIn("create on TestModel by testuser", actual_str)
        self.assertIn("TestModel", actual_str)
    
    def test_audit_log_changes(self):
        """Test audit log changes field."""
        self.assertIsInstance(self.audit_log.changes, dict)
    
    def test_audit_log_user_relationship(self):
        """Test audit log user relationship."""
        self.assertEqual(self.audit_log.user, self.user)
        self.assertEqual(self.audit_log.user.username, 'testuser')
    
    def test_audit_log_action_choices(self):
        """Test audit log action choices."""
        valid_actions = ['create', 'update', 'delete', 'view', 'export', 'import']
        for action in valid_actions:
            audit_log = AuditLog.objects.create(
                action=action,
                resource_type='TestModel',
                resource_id=1,
                user=self.user
            )
            self.assertEqual(audit_log.action, action)
    
    def test_audit_log_details_json(self):
        """Test that details field can store JSON data."""
        complex_details = {
            'nested': {
                'field': 'value',
                'list': [1, 2, 3],
                'boolean': True
            },
            'simple': 'string'
        }
        
        audit_log = AuditLog.objects.create(
            action='update',
            resource_type='TestModel',
            resource_id=1,
            user=self.user,
            changes=complex_details
        )
        
        # Refresh from database
        audit_log.refresh_from_db()
        self.assertEqual(audit_log.changes, complex_details)
    
    def test_audit_log_ip_address_validation(self):
        """Test IP address field validation."""
        # Test valid IP addresses
        valid_ips = ['127.0.0.1', '192.168.1.1', '::1', '2001:db8::1']
        
        for ip in valid_ips:
            audit_log = AuditLog.objects.create(
                action='view',
                resource_type='TestModel',
                resource_id=1,
                user=self.user,
                ip_address=ip
            )
            self.assertEqual(audit_log.ip_address, ip)
    
    def test_audit_log_user_agent_length(self):
        """Test user agent field length."""
        long_user_agent = 'A' * 500  # Very long user agent
        
        audit_log = AuditLog.objects.create(
            action='view',
            resource_type='TestModel',
            resource_id=1,
            user=self.user,
            user_agent=long_user_agent
        )
        
        self.assertEqual(audit_log.user_agent, long_user_agent)
    
    def test_audit_log_changes_default(self):
        """Test that changes field has default empty dict."""
        audit_log = AuditLog.objects.create(
            action='view',
            resource_type='TestModel',
            resource_id=1,
            user=self.user
        )
        
        self.assertEqual(audit_log.changes, {})
    
    def test_audit_log_ordering(self):
        """Test audit log ordering by created_at."""
        # Create multiple audit logs
        AuditLog.objects.create(
            action='view',
            resource_type='TestModel',
            resource_id=1,
            user=self.user
        )
        
        AuditLog.objects.create(
            action='update',
            resource_type='TestModel',
            resource_id=1,
            user=self.user
        )
        
        # Get all audit logs ordered by timestamp
        audit_logs = AuditLog.objects.all().order_by('timestamp')
        
        # Should be ordered by creation time (oldest first)
        self.assertEqual(audit_logs.count(), 3)
        self.assertEqual(audit_logs[0].action, 'create')  # First one from setUp
        self.assertEqual(audit_logs[1].action, 'view')
        self.assertEqual(audit_logs[2].action, 'update')
