from rest_framework import serializers
from .models import Document, DocumentVersion
from users.serializers import UserListSerializer
from projects.serializers import ProjectListSerializer
from projects.models import Project


class DocumentVersionSerializer(serializers.ModelSerializer):
    """Document version serializer."""

    changed_by = UserListSerializer(read_only=True)
    diff_summary_display = serializers.CharField(
        source="get_diff_summary", read_only=True
    )

    class Meta:
        model = DocumentVersion
        fields = [
            "id",
            "version_number",
            "content",
            "change_summary",
            "changed_by",
            "changed_at",
            "diff_summary",
            "diff_summary_display",
        ]
        read_only_fields = ["id", "version_number", "changed_by", "changed_at"]


class DocumentSerializer(serializers.ModelSerializer):
    """Document serializer."""

    project = ProjectListSerializer(read_only=True)
    created_by = UserListSerializer(read_only=True)
    updated_by = UserListSerializer(read_only=True)
    processing_time_display = serializers.CharField(
        source="get_processing_time_display", read_only=True
    )

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "description",
            "content",
            "project",
            "file",
            "file_name",
            "file_size",
            "content_type",
            "encoding",
            "processing_status",
            "processing_started_at",
            "processing_completed_at",
            "processing_time_display",
            "word_count",
            "character_count",
            "line_count",
            "language",
            "total_entities",
            "verified_entities",
            "unverified_entities",
            "confidence_score",
            "quality_score",
            "tags",
            "metadata",
            "notes",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "processing_started_at",
            "processing_completed_at",
            "processing_time_display",
            "word_count",
            "character_count",
            "line_count",
            "total_entities",
            "verified_entities",
            "unverified_entities",
        ]


class DocumentCreateSerializer(serializers.ModelSerializer):
    """Document creation serializer."""

    # Override project field to accept ID
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True
    )

    class Meta:
        model = Document
        fields = [
            "title",
            "description",
            "content",
            "project",
            "file",
            "language",
            "tags",
            "metadata",
            "notes",
        ]

    def validate(self, attrs):
        """Validate document data."""
        if not attrs.get("content") and not attrs.get("file"):
            raise serializers.ValidationError("Either content or file must be provided")
        return attrs


class DocumentUpdateSerializer(serializers.ModelSerializer):
    """Document update serializer."""

    class Meta:
        model = Document
        fields = [
            "title",
            "description",
            "content",
            "language",
            "tags",
            "metadata",
            "notes",
        ]


class DocumentListSerializer(serializers.ModelSerializer):
    """Document list serializer."""

    project = ProjectListSerializer(read_only=True)
    created_by = UserListSerializer(read_only=True)
    processing_time_display = serializers.CharField(
        source="get_processing_time_display", read_only=True
    )

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "description",
            "project",
            "processing_status",
            "word_count",
            "line_count",
            "language",
            "total_entities",
            "verified_entities",
            "unverified_entities",
            "created_by",
            "created_at",
            "processing_time_display",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "word_count",
            "line_count",
            "total_entities",
            "verified_entities",
            "unverified_entities",
        ]


class DocumentDetailSerializer(DocumentSerializer):
    """Document detail serializer with versions."""

    versions = DocumentVersionSerializer(many=True, read_only=True)

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ["versions"]


class DocumentUploadSerializer(serializers.Serializer):
    """Document upload serializer."""

    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    project = serializers.IntegerField()
    file = serializers.FileField(required=False)
    content = serializers.CharField(required=False, allow_blank=True)
    language = serializers.CharField(max_length=10, default="ur")
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    metadata = serializers.DictField(required=False)

    def validate(self, attrs):
        """Validate upload data."""
        if not attrs.get("file") and not attrs.get("content"):
            raise serializers.ValidationError("Either file or content must be provided")
        return attrs


class DocumentProcessingSerializer(serializers.Serializer):
    """Document processing serializer."""

    llm_config = serializers.IntegerField(required=False)
    chunk_size = serializers.IntegerField(required=False, min_value=100, max_value=5000)
    overlap_size = serializers.IntegerField(required=False, min_value=0, max_value=1000)
    confidence_threshold = serializers.FloatField(
        required=False, min_value=0.0, max_value=1.0
    )
    entity_types = serializers.ListField(child=serializers.CharField(), required=False)
    prompt_type = serializers.ChoiceField(
        choices=["general_ner", "urdu_ner", "marsiya_ner", "custom"], required=False
    )
    custom_prompt = serializers.CharField(required=False, allow_blank=True)


class DocumentStatsSerializer(serializers.Serializer):
    """Document statistics serializer."""

    total_documents = serializers.IntegerField()
    processing_status_breakdown = serializers.DictField()
    language_breakdown = serializers.DictField()
    entity_counts = serializers.DictField()
    average_processing_time = serializers.CharField()
    recent_uploads = serializers.ListField()
