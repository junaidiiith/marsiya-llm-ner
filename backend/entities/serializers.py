from rest_framework import serializers
from .models import EntityType, Entity, EntityRelationship
from users.serializers import UserListSerializer
from documents.serializers import DocumentListSerializer


class EntityTypeSerializer(serializers.ModelSerializer):
    """Entity type serializer."""

    examples_display = serializers.CharField(
        source="get_examples_display", read_only=True
    )
    validation_rules_display = serializers.CharField(
        source="get_validation_rules_display", read_only=True
    )
    entities_count = serializers.IntegerField(
        source="get_entities_count", read_only=True
    )
    verified_entities_count = serializers.IntegerField(
        source="get_verified_entities_count", read_only=True
    )

    class Meta:
        model = EntityType
        fields = [
            "id",
            "name",
            "display_name",
            "description",
            "color_code",
            "icon",
            "is_active",
            "is_system",
            "sort_order",
            "validation_rules",
            "examples",
            "examples_display",
            "validation_rules_display",
            "entities_count",
            "verified_entities_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EntityTypeCreateSerializer(serializers.ModelSerializer):
    """Entity type creation serializer."""

    class Meta:
        model = EntityType
        fields = [
            "name",
            "display_name",
            "description",
            "color_code",
            "icon",
            "is_active",
            "is_system",
            "sort_order",
            "validation_rules",
            "examples",
        ]


class EntityTypeUpdateSerializer(serializers.ModelSerializer):
    """Entity type update serializer."""

    class Meta:
        model = EntityType
        fields = [
            "display_name",
            "description",
            "color_code",
            "icon",
            "is_active",
            "sort_order",
            "validation_rules",
            "examples",
        ]


class EntitySerializer(serializers.ModelSerializer):
    """Entity serializer."""

    entity_type = EntityTypeSerializer(read_only=True)
    document = DocumentListSerializer(read_only=True)
    created_by = UserListSerializer(read_only=True)
    updated_by = UserListSerializer(read_only=True)
    verified_by = UserListSerializer(read_only=True)

    class Meta:
        model = Entity
        fields = [
            "id",
            "text",
            "entity_type",
            "document",
            "start_position",
            "end_position",
            "line_number",
            "word_position",
            "confidence_score",
            "quality_score",
            "is_verified",
            "verified_by",
            "verified_at",
            "verification_notes",
            "source",
            "context_before",
            "context_after",
            "tags",
            "attributes",
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
            "verified_by",
            "verified_at",
            "context_before",
            "context_after",
        ]


class EntityCreateSerializer(serializers.ModelSerializer):
    """Entity creation serializer."""

    class Meta:
        model = Entity
        fields = [
            "text",
            "entity_type",
            "document",
            "start_position",
            "end_position",
            "line_number",
            "word_position",
            "confidence_score",
            "quality_score",
            "source",
            "tags",
            "attributes",
            "notes",
        ]


class EntityUpdateSerializer(serializers.ModelSerializer):
    """Entity update serializer."""

    class Meta:
        model = Entity
        fields = [
            "text",
            "entity_type",
            "start_position",
            "end_position",
            "line_number",
            "word_position",
            "quality_score",
            "tags",
            "attributes",
            "notes",
        ]


class EntityListSerializer(serializers.ModelSerializer):
    """Entity list serializer."""

    entity_type = EntityTypeSerializer(read_only=True)
    document = DocumentListSerializer(read_only=True)
    created_by = UserListSerializer(read_only=True)

    class Meta:
        model = Entity
        fields = [
            "id",
            "text",
            "entity_type",
            "document",
            "line_number",
            "confidence_score",
            "is_verified",
            "source",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]


class EntityVerificationSerializer(serializers.Serializer):
    """Entity verification serializer."""

    is_verified = serializers.BooleanField()
    verification_notes = serializers.CharField(required=False, allow_blank=True)


class EntityBulkUpdateSerializer(serializers.Serializer):
    """Entity bulk update serializer."""

    entity_ids = serializers.ListField(child=serializers.IntegerField())
    entity_type = serializers.IntegerField(required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    attributes = serializers.DictField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)


class EntityRelationshipSerializer(serializers.ModelSerializer):
    """Entity relationship serializer."""

    source_entity = EntitySerializer(read_only=True)
    target_entity = EntitySerializer(read_only=True)
    source_entity_id = serializers.IntegerField(write_only=True)
    target_entity_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = EntityRelationship
        fields = [
            "id",
            "source_entity",
            "target_entity",
            "source_entity_id",
            "target_entity_id",
            "relationship_type",
            "confidence_score",
            "is_verified",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class EntityRelationshipCreateSerializer(serializers.ModelSerializer):
    """Entity relationship creation serializer."""

    class Meta:
        model = EntityRelationship
        fields = [
            "source_entity",
            "target_entity",
            "relationship_type",
            "confidence_score",
            "notes",
        ]

    def validate(self, attrs):
        """Validate relationship data."""
        source = attrs["source_entity"]
        target = attrs["target_entity"]

        if source == target:
            raise serializers.ValidationError(
                "Source and target entities cannot be the same"
            )

        if source.document != target.document:
            raise serializers.ValidationError("Entities must be from the same document")

        return attrs


class EntityRelationshipUpdateSerializer(serializers.ModelSerializer):
    """Entity relationship update serializer."""

    class Meta:
        model = EntityRelationship
        fields = ["relationship_type", "confidence_score", "is_verified", "notes"]


class EntitySearchSerializer(serializers.Serializer):
    """Entity search serializer."""

    text = serializers.CharField(required=False)
    entity_type = serializers.IntegerField(required=False)
    document = serializers.IntegerField(required=False)
    project = serializers.IntegerField(required=False)
    is_verified = serializers.BooleanField(required=False)
    source = serializers.CharField(required=False)
    confidence_min = serializers.FloatField(
        required=False, min_value=0.0, max_value=1.0
    )
    confidence_max = serializers.FloatField(
        required=False, min_value=0.0, max_value=1.0
    )
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    created_after = serializers.DateTimeField(required=False)
    created_before = serializers.DateTimeField(required=False)


class EntityStatsSerializer(serializers.Serializer):
    """Entity statistics serializer."""

    total_entities = serializers.IntegerField()
    verified_entities = serializers.IntegerField()
    unverified_entities = serializers.IntegerField()
    entity_type_breakdown = serializers.DictField()
    source_breakdown = serializers.DictField()
    confidence_distribution = serializers.DictField()
    verification_rate = serializers.FloatField()
    recent_entities = serializers.ListField()

