"""
Unit tests for core views.
"""

import pytest
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from core.models import AuditLog
from core.views import (
    system_health,
    system_info,
    database_stats,
    clear_cache,
    user_activity_summary,
    export_request,
    import_request,
)

User = get_user_model()


class TestSystemHealthView(TestCase):
    """Test system health view."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.factory = RequestFactory()

    @patch("core.views.psutil.cpu_percent")
    @patch("core.views.psutil.virtual_memory")
    @patch("core.views.psutil.disk_usage")
    def test_system_health_success(self, mock_disk, mock_memory, mock_cpu):
        """Test successful system health check."""
        # Mock system resources
        mock_cpu.return_value = 25.5
        mock_memory.return_value = MagicMock(percent=65.2, available=8589934592)  # 8GB
        mock_disk.return_value = MagicMock(percent=45.0, free=107374182400)  # 100GB

        url = reverse("core:system_health")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        # Check response structure
        self.assertIn("timestamp", data)
        self.assertIn("status", data)
        self.assertIn("system_resources", data)
        self.assertIn("django_settings", data)

        # Check status
        self.assertIn("database", data["status"])
        self.assertIn("cache", data["status"])
        self.assertIn("overall", data["status"])

        # Check system resources
        resources = data["system_resources"]
        self.assertEqual(resources["cpu_percent"], 25.5)
        self.assertEqual(resources["memory_percent"], 65.2)
        self.assertEqual(resources["disk_percent"], 45.0)

    def test_system_health_unauthorized(self):
        """Test system health without authentication."""
        client = APIClient()
        url = reverse("core:system_health")
        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_system_health_non_admin(self):
        """Test system health with non-admin user."""
        user = User.objects.create_user(
            username="regular", email="regular@example.com", password="regularpass123"
        )
        self.client.force_authenticate(user=user)

        url = reverse("core:system_health")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestAuditLogViews(TestCase):
    """Test audit log views."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            is_staff=True,
            is_superuser=True,
        )
        self.regular_user = User.objects.create_user(
            username="regular", email="regular@example.com", password="regularpass123"
        )

        # Create test audit logs
        self.audit_log1 = AuditLog.objects.create(
            action="CREATE",
            model_name="TestModel",
            object_id=1,
            user=self.admin_user,
            details={"field": "value1"},
        )

        self.audit_log2 = AuditLog.objects.create(
            action="UPDATE",
            model_name="TestModel",
            object_id=1,
            user=self.regular_user,
            details={"field": "value2"},
        )

        self.client.force_authenticate(user=self.admin_user)

    def test_audit_log_list(self):
        """Test audit log list view."""
        url = reverse("core:audit_log_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_audit_log_detail(self):
        """Test audit log detail view."""
        url = reverse("core:audit_log_detail", kwargs={"pk": self.audit_log1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "CREATE")
        self.assertEqual(response.data["model_name"], "TestModel")

    def test_audit_log_filter(self):
        """Test audit log filter view."""
        url = reverse("core:audit_log_filter")
        response = self.client.get(
            url,
            {"action": "CREATE", "model_name": "TestModel", "user": self.admin_user.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["action"], "CREATE")

    def test_audit_log_stats(self):
        """Test audit log statistics view."""
        url = reverse("core:audit_log_stats")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_logs", response.data)
        self.assertIn("actions_summary", response.data)
        self.assertIn("models_summary", response.data)

    def test_audit_log_unauthorized(self):
        """Test audit log access without authentication."""
        client = APIClient()
        url = reverse("core:audit_log_list")
        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_audit_log_non_admin(self):
        """Test audit log access with non-admin user."""
        self.client.force_authenticate(user=self.regular_user)

        url = reverse("core:audit_log_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestSystemAdminViews(TestCase):
    """Test system administration views."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_system_info(self):
        """Test system info view."""
        url = reverse("core:system_info")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("django_version", response.data)
        self.assertIn("python_version", response.data)
        self.assertIn("database_info", response.data)

    def test_database_stats(self):
        """Test database statistics view."""
        url = reverse("core:database_stats")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_tables", response.data)
        self.assertIn("database_size", response.data)

    @patch("core.views.cache.clear")
    def test_clear_cache(self, mock_cache_clear):
        """Test clear cache view."""
        mock_cache_clear.return_value = None

        url = reverse("core:clear_cache")
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_cache_clear.assert_called_once()

    def test_user_activity_summary(self):
        """Test user activity summary view."""
        url = reverse("core:user_activity_summary")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_users", response.data)
        self.assertIn("active_users", response.data)
        self.assertIn("recent_activity", response.data)


class TestDataManagementViews(TestCase):
    """Test data management views."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_export_request(self):
        """Test export request view."""
        url = reverse("core:export_request")
        data = {
            "export_type": "audit_logs",
            "format": "json",
            "filters": {"action": "CREATE"},
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertIn("export_type", response.data)
        self.assertIn("format", response.data)

    def test_import_request(self):
        """Test import request view."""
        url = reverse("core:import_request")
        data = {
            "import_type": "users",
            "file_path": "/tmp/test.csv",
            "options": {"create_missing": True},
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertIn("import_type", response.data)

    def test_export_request_validation(self):
        """Test export request validation."""
        url = reverse("core:export_request")

        # Test invalid export type
        data = {"export_type": "invalid_type"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_import_request_validation(self):
        """Test import request validation."""
        url = reverse("core:import_request")

        # Test missing required fields
        data = {}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestCoreViewsIntegration(TestCase):
    """Integration tests for core views."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_system_health_with_audit_logs(self):
        """Test system health when audit logs exist."""
        # Create some audit logs
        AuditLog.objects.create(
            action="CREATE", model_name="TestModel", object_id=1, user=self.admin_user
        )

        url = reverse("core:system_health")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"]["overall"], "healthy")

    def test_audit_log_workflow(self):
        """Test complete audit log workflow."""
        # Create audit log
        audit_log = AuditLog.objects.create(
            action="CREATE", model_name="TestModel", object_id=1, user=self.admin_user
        )

        # List audit logs
        list_url = reverse("core:core:audit_log_list")
        list_response = self.client.get(list_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        # Get audit log detail
        detail_url = reverse("core:audit_log_detail", kwargs={"pk": audit_log.pk})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)

        # Get audit log stats
        stats_url = reverse("core:audit_log_stats")
        stats_response = self.client.get(stats_url)
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)

    def test_system_admin_workflow(self):
        """Test complete system administration workflow."""
        # Get system info
        info_url = reverse("core:system_info")
        info_response = self.client.get(info_url)
        self.assertEqual(info_response.status_code, status.HTTP_200_OK)

        # Get database stats
        db_url = reverse("core:database_stats")
        db_response = self.client.get(db_url)
        self.assertEqual(db_response.status_code, status.HTTP_200_OK)

        # Get user activity summary
        activity_url = reverse("core:user_activity_summary")
        activity_response = self.client.get(activity_url)
        self.assertEqual(activity_response.status_code, status.HTTP_200_OK)
