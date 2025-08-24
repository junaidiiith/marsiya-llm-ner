from rest_framework import serializers
from .models import ProcessingJob
from users.serializers import UserListSerializer
from documents.serializers import DocumentListSerializer
from projects.serializers import ProjectListSerializer


class ProcessingJobSerializer(serializers.ModelSerializer):
    """Processing job serializer."""

    created_by = UserListSerializer(read_only=True)
    updated_by = UserListSerializer(read_only=True)
    document = DocumentListSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    processing_time_display = serializers.CharField(
        source="get_processing_time_display", read_only=True
    )
    status_display_with_progress = serializers.CharField(
        source="get_status_display_with_progress", read_only=True
    )

    class Meta:
        model = ProcessingJob
        fields = [
            "id",
            "job_id",
            "name",
            "description",
            "job_type",
            "document",
            "project",
            "status",
            "progress",
            "total_steps",
            "current_step",
            "started_at",
            "completed_at",
            "estimated_completion",
            "processing_time_display",
            "result",
            "error_message",
            "error_details",
            "memory_usage",
            "cpu_usage",
            "priority",
            "retry_count",
            "max_retries",
            "tags",
            "notes",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "status_display_with_progress",
        ]
        read_only_fields = [
            "id",
            "job_id",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "started_at",
            "completed_at",
            "processing_time_display",
        ]


class ProcessingJobCreateSerializer(serializers.ModelSerializer):
    """Processing job creation serializer."""

    class Meta:
        model = ProcessingJob
        fields = [
            "name",
            "description",
            "job_type",
            "document",
            "project",
            "priority",
            "max_retries",
            "tags",
            "notes",
        ]


class ProcessingJobUpdateSerializer(serializers.ModelSerializer):
    """Processing job update serializer."""

    class Meta:
        model = ProcessingJob
        fields = ["name", "description", "priority", "tags", "notes"]


class ProcessingJobListSerializer(serializers.ModelSerializer):
    """Processing job list serializer."""

    created_by = UserListSerializer(read_only=True)
    document = DocumentListSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    processing_time_display = serializers.CharField(
        source="get_processing_time_display", read_only=True
    )
    status_display_with_progress = serializers.CharField(
        source="get_status_display_with_progress", read_only=True
    )

    class Meta:
        model = ProcessingJob
        fields = [
            "id",
            "job_id",
            "name",
            "job_type",
            "status",
            "progress",
            "current_step",
            "started_at",
            "completed_at",
            "processing_time_display",
            "priority",
            "retry_count",
            "created_by",
            "created_at",
            "status_display_with_progress",
            "document",
            "project",
        ]
        read_only_fields = [
            "id",
            "job_id",
            "created_by",
            "created_at",
            "started_at",
            "completed_at",
        ]


class ProcessingJobDetailSerializer(ProcessingJobSerializer):
    """Processing job detail serializer."""

    class Meta(ProcessingJobSerializer.Meta):
        fields = ProcessingJobSerializer.Meta.fields


class ProcessingJobProgressSerializer(serializers.Serializer):
    """Processing job progress update serializer."""

    progress = serializers.IntegerField(min_value=0, max_value=100)
    current_step = serializers.CharField(required=False, allow_blank=True)
    estimated_completion = serializers.DateTimeField(required=False)


class ProcessingJobResultSerializer(serializers.Serializer):
    """Processing job result serializer."""

    result = serializers.DictField(required=False)
    error_message = serializers.CharField(required=False, allow_blank=True)
    error_details = serializers.DictField(required=False)
    memory_usage = serializers.IntegerField(required=False, min_value=0)
    cpu_usage = serializers.FloatField(required=False, min_value=0.0, max_value=100.0)


class ProcessingJobActionSerializer(serializers.Serializer):
    """Processing job action serializer."""

    action = serializers.ChoiceField(choices=["start", "cancel", "retry", "reset"])


class ProcessingJobFilterSerializer(serializers.Serializer):
    """Processing job filter serializer."""

    job_type = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    priority = serializers.IntegerField(required=False)
    created_by = serializers.IntegerField(required=False)
    document = serializers.IntegerField(required=False)
    project = serializers.IntegerField(required=False)
    created_after = serializers.DateTimeField(required=False)
    created_before = serializers.DateTimeField(required=False)
    is_active = serializers.BooleanField(required=False)


class ProcessingJobStatsSerializer(serializers.Serializer):
    """Processing job statistics serializer."""

    total_jobs = serializers.IntegerField()
    completed_jobs = serializers.IntegerField()
    failed_jobs = serializers.IntegerField()
    running_jobs = serializers.IntegerField()
    pending_jobs = serializers.IntegerField()
    success_rate = serializers.FloatField()
    average_processing_time = serializers.CharField()
    job_type_breakdown = serializers.DictField()
    status_breakdown = serializers.DictField()
    recent_jobs = serializers.ListField()


class ProcessingJobBulkActionSerializer(serializers.Serializer):
    """Processing job bulk action serializer."""

    job_ids = serializers.ListField(child=serializers.IntegerField())
    action = serializers.ChoiceField(choices=["cancel", "retry", "reset", "delete"])

