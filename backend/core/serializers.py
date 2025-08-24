from rest_framework import serializers
from .models import AuditLog
from users.serializers import UserListSerializer
from projects.serializers import ProjectListSerializer


class AuditLogSerializer(serializers.ModelSerializer):
    """Audit log serializer."""

    user = UserListSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "timestamp",
            "user",
            "action",
            "resource_type",
            "resource_id",
            "resource_name",
            "changes",
            "ip_address",
            "user_agent",
            "project",
            "session_id",
        ]
        read_only_fields = ["id", "timestamp"]


class AuditLogListSerializer(serializers.ModelSerializer):
    """Audit log list serializer."""

    user = UserListSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "timestamp",
            "user",
            "action",
            "resource_type",
            "resource_name",
            "project",
            "ip_address",
        ]
        read_only_fields = ["id", "timestamp"]


class AuditLogFilterSerializer(serializers.Serializer):
    """Audit log filter serializer."""

    user = serializers.IntegerField(required=False)
    action = serializers.CharField(required=False)
    resource_type = serializers.CharField(required=False)
    project = serializers.IntegerField(required=False)
    timestamp_after = serializers.DateTimeField(required=False)
    timestamp_before = serializers.DateTimeField(required=False)
    ip_address = serializers.CharField(required=False)


class AuditLogStatsSerializer(serializers.Serializer):
    """Audit log statistics serializer."""

    total_logs = serializers.IntegerField()
    action_breakdown = serializers.DictField()
    resource_type_breakdown = serializers.DictField()
    user_breakdown = serializers.DictField()
    recent_activity = serializers.ListField()
    activity_trend = serializers.ListField()


class SystemHealthSerializer(serializers.Serializer):
    """System health serializer."""

    database_status = serializers.CharField()
    redis_status = serializers.CharField()
    celery_status = serializers.CharField()
    storage_status = serializers.CharField()
    memory_usage = serializers.DictField()
    disk_usage = serializers.DictField()
    active_users = serializers.IntegerField()
    active_jobs = serializers.IntegerField()
    uptime = serializers.CharField()
    last_backup = serializers.DateTimeField(required=False)


class ExportRequestSerializer(serializers.Serializer):
    """Export request serializer."""

    export_type = serializers.ChoiceField(choices=["excel", "csv", "json"])
    data_type = serializers.ChoiceField(
        choices=["entities", "documents", "projects", "audit_logs"]
    )
    filters = serializers.DictField(required=False)
    include_metadata = serializers.BooleanField(default=True)
    format_options = serializers.DictField(required=False)


class ImportRequestSerializer(serializers.Serializer):
    """Import request serializer."""

    import_type = serializers.ChoiceField(choices=["entities", "documents", "projects"])
    file = serializers.FileField()
    options = serializers.DictField(required=False)
    validate_only = serializers.BooleanField(default=False)
    create_missing = serializers.BooleanField(default=True)

