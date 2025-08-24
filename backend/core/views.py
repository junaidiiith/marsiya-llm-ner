from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Max
from django.utils import timezone
from django.core.cache import cache
from django.db import connection
from django.conf import settings

import psutil
import os
from .models import AuditLog
from .serializers import (
    AuditLogSerializer,
    AuditLogListSerializer,
    AuditLogFilterSerializer,
    AuditLogStatsSerializer,
    SystemHealthSerializer,
    ExportRequestSerializer,
    ImportRequestSerializer,
)


class AuditLogListView(generics.ListAPIView):
    """List audit logs with filtering."""

    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AuditLogListSerializer
    queryset = AuditLog.objects.all().order_by("-timestamp")

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by user
        user_id = self.request.query_params.get("user_id")
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by action
        action = self.request.query_params.get("action")
        if action:
            queryset = queryset.filter(action=action)

        # Filter by model
        model = self.request.query_params.get("model")
        if model:
            queryset = queryset.filter(model=model)

        # Filter by object_id
        object_id = self.request.query_params.get("object_id")
        if object_id:
            queryset = queryset.filter(object_id=object_id)

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)

        end_date = self.request.query_params.get("end_date")
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        # Filter by IP address
        ip_address = self.request.query_params.get("ip_address")
        if ip_address:
            queryset = queryset.filter(ip_address__icontains=ip_address)

        return queryset


class AuditLogDetailView(generics.RetrieveAPIView):
    """Get audit log details."""

    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AuditLogSerializer
    queryset = AuditLog.objects.all()


class AuditLogFilterView(generics.ListAPIView):
    """Advanced audit log filtering."""

    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AuditLogListSerializer

    def get_queryset(self):
        serializer = AuditLogFilterSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)

        filters = serializer.validated_data
        queryset = AuditLog.objects.all()

        # Apply filters
        if filters.get("user_id"):
            queryset = queryset.filter(user_id=filters["user_id"])

        if filters.get("action"):
            queryset = queryset.filter(action__in=filters["action"])

        if filters.get("model"):
            queryset = queryset.filter(model__in=filters["model"])

        if filters.get("object_id"):
            queryset = queryset.filter(object_id__in=filters["object_id"])

        if filters.get("start_date"):
            queryset = queryset.filter(timestamp__gte=filters["start_date"])

        if filters.get("end_date"):
            queryset = queryset.filter(timestamp__lte=filters["end_date"])

        if filters.get("ip_address"):
            queryset = queryset.filter(ip_address__icontains=filters["ip_address"])

        if filters.get("success"):
            queryset = queryset.filter(success=filters["success"])

        # Order by
        order_by = filters.get("order_by", "-timestamp")
        queryset = queryset.order_by(order_by)

        return queryset


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def audit_log_stats(request):
    """Get audit log statistics."""
    # Overall statistics
    total_logs = AuditLog.objects.count()

    # Action distribution
    action_stats = (
        AuditLog.objects.values("action")
        .annotate(
            count=Count("id"),
            success_count=Count("id", filter=Q(success=True)),
            failure_count=Count("id", filter=Q(success=False)),
        )
        .order_by("-count")
    )

    # Model distribution
    model_stats = (
        AuditLog.objects.values("model").annotate(count=Count("id")).order_by("-count")
    )

    # User activity
    user_stats = (
        AuditLog.objects.values("user__username")
        .annotate(
            total_actions=Count("id"),
            successful_actions=Count("id", filter=Q(success=True)),
            failed_actions=Count("id", filter=Q(success=False)),
        )
        .order_by("-total_actions")
    )

    # Success rate
    success_rate = AuditLog.objects.filter(success=True).count()
    failure_rate = total_logs - success_rate

    # Recent activity
    recent_logs = AuditLog.objects.filter(
        timestamp__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()

    # IP address distribution
    ip_stats = (
        AuditLog.objects.values("ip_address")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    stats = {
        "total_logs": total_logs,
        "success_rate": (success_rate / total_logs * 100) if total_logs > 0 else 0,
        "failure_rate": (failure_rate / total_logs * 100) if total_logs > 0 else 0,
        "action_distribution": list(action_stats),
        "model_distribution": list(model_stats),
        "user_activity": list(user_stats),
        "recent_activity": recent_logs,
        "top_ip_addresses": list(ip_stats),
    }

    serializer = AuditLogStatsSerializer(stats)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def system_health(request):
    """Get system health information."""
    # Database health
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
            db_response_time = None
    except Exception as e:
        db_status = "unhealthy"
        db_response_time = None

    # Cache health
    try:
        cache.set("health_check", "ok", 10)
        cache_status = "healthy" if cache.get("health_check") == "ok" else "unhealthy"
    except Exception:
        cache_status = "unhealthy"

    # System resources
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        system_resources = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2),
        }
    except Exception:
        system_resources = None

    # Django settings health
    django_health = {
        "debug_mode": settings.DEBUG,
        "database_engine": settings.DATABASES["default"]["ENGINE"],
        "cache_backend": getattr(settings, "CACHES", {})
        .get("default", {})
        .get("BACKEND"),
        "static_root": getattr(settings, "STATIC_ROOT", None),
        "media_root": getattr(settings, "MEDIA_ROOT", None),
    }

    # Application status
    app_status = {
        "database": db_status,
        "cache": cache_status,
        "system_resources": system_resources is not None,
        "overall": "healthy"
        if all([db_status == "healthy", cache_status == "healthy"])
        else "degraded",
    }

    health_data = {
        "timestamp": timezone.now(),
        "status": app_status,
        "system_resources": system_resources,
        "django_settings": django_health,
    }

    serializer = SystemHealthSerializer(health_data)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def export_request(request):
    """Request data export."""
    serializer = ExportRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    export_type = serializer.validated_data["export_type"]
    filters = serializer.validated_data.get("filters", {})
    format_type = serializer.validated_data.get("format", "json")

    # In a real implementation, you would queue this for background processing
    # For now, we'll just return a success message

    return Response(
        {
            "message": "Export request submitted successfully",
            "export_type": export_type,
            "format": format_type,
            "filters": filters,
            "estimated_completion": timezone.now() + timezone.timedelta(minutes=30),
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def import_request(request):
    """Request data import."""
    serializer = ImportRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    import_type = serializer.validated_data["import_type"]
    file_path = serializer.validated_data.get("file_path")
    options = serializer.validated_data.get("options", {})

    # In a real implementation, you would queue this for background processing
    # For now, we'll just return a success message

    return Response(
        {
            "message": "Import request submitted successfully",
            "import_type": import_type,
            "file_path": file_path,
            "options": options,
            "estimated_completion": timezone.now() + timezone.timedelta(minutes=45),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def system_info(request):
    """Get detailed system information."""
    # Python and Django info
    import sys
    import django

    python_info = {
        "version": sys.version,
        "executable": sys.executable,
        "platform": sys.platform,
    }

    django_info = {
        "version": django.get_version(),
        "settings_module": settings.SETTINGS_MODULE,
        "installed_apps_count": len(settings.INSTALLED_APPS),
    }

    # Database info
    db_info = {
        "engine": settings.DATABASES["default"]["ENGINE"],
        "name": settings.DATABASES["default"].get("NAME"),
        "host": settings.DATABASES["default"].get("HOST"),
        "port": settings.DATABASES["default"].get("PORT"),
    }

    # Cache info
    cache_info = {
        "backend": getattr(settings, "CACHES", {}).get("default", {}).get("BACKEND"),
        "location": getattr(settings, "CACHES", {}).get("default", {}).get("LOCATION"),
    }

    # File system info
    try:
        static_root = getattr(settings, "STATIC_ROOT", None)
        media_root = getattr(settings, "MEDIA_ROOT", None)

        file_system_info = {
            "static_root": static_root,
            "static_root_exists": os.path.exists(static_root) if static_root else False,
            "media_root": media_root,
            "media_root_exists": os.path.exists(media_root) if media_root else False,
            "current_working_directory": os.getcwd(),
        }
    except Exception:
        file_system_info = None

    system_info = {
        "python": python_info,
        "django": django_info,
        "database": db_info,
        "cache": cache_info,
        "file_system": file_system_info,
        "timestamp": timezone.now(),
    }

    return Response(system_info)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def database_stats(request):
    """Get database statistics."""
    try:
        with connection.cursor() as cursor:
            # Get table sizes
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE schemaname = 'public'
                ORDER BY tablename, attname
            """)
            table_stats = cursor.fetchall()

            # Get database size
            cursor.execute("""
                SELECT 
                    pg_size_pretty(pg_database_size(current_database())) as db_size,
                    pg_database_size(current_database()) as db_size_bytes
            """)
            db_size = cursor.fetchone()

            # Get table sizes
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size,
                    pg_total_relation_size(schemaname||'.'||tablename) as table_size_bytes
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)
            table_sizes = cursor.fetchall()

            db_stats = {
                "database_size": db_size[0] if db_size else "Unknown",
                "database_size_bytes": db_size[1] if db_size else 0,
                "table_statistics": table_stats,
                "table_sizes": table_sizes,
            }

    except Exception as e:
        db_stats = {
            "error": str(e),
            "database_size": "Unknown",
            "table_statistics": [],
            "table_sizes": [],
        }

    return Response(db_stats)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def clear_cache(request):
    """Clear system cache."""
    try:
        cache.clear()
        return Response(
            {"message": "Cache cleared successfully", "timestamp": timezone.now()}
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to clear cache: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_activity_summary(request):
    """Get user activity summary."""
    # Recent user activity
    recent_activity = (
        AuditLog.objects.filter(
            timestamp__gte=timezone.now() - timezone.timedelta(days=7)
        )
        .values("user__username")
        .annotate(action_count=Count("id"), last_activity=Max("timestamp"))
        .order_by("-action_count")
    )

    # Most active users
    most_active_users = (
        AuditLog.objects.values("user__username")
        .annotate(
            total_actions=Count("id"),
            successful_actions=Count("id", filter=Q(success=True)),
            failed_actions=Count("id", filter=Q(success=False)),
        )
        .order_by("-total_actions")[:10]
    )

    # Action patterns
    action_patterns = (
        AuditLog.objects.values("action")
        .annotate(count=Count("id"), unique_users=Count("user", distinct=True))
        .order_by("-count")
    )

    summary = {
        "recent_activity": list(recent_activity),
        "most_active_users": list(most_active_users),
        "action_patterns": list(action_patterns),
        "period": "7 days",
        "timestamp": timezone.now(),
    }

    return Response(summary)
