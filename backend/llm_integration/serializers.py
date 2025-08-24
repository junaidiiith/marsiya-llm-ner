from rest_framework import serializers
from .models import LLMModel, LLMProcessingConfig
from users.serializers import UserListSerializer


class LLMModelSerializer(serializers.ModelSerializer):
    """LLM model serializer."""

    created_by = UserListSerializer(read_only=True)
    updated_by = UserListSerializer(read_only=True)
    success_rate = serializers.FloatField(source="get_success_rate", read_only=True)
    failure_rate = serializers.FloatField(source="get_failure_rate", read_only=True)

    class Meta:
        model = LLMModel
        fields = [
            "id",
            "name",
            "description",
            "provider",
            "model_name",
            "api_key",
            "api_base_url",
            "settings",
            "is_active",
            "is_default",
            "priority",
            "total_requests",
            "successful_requests",
            "failed_requests",
            "average_response_time",
            "rate_limit_per_hour",
            "rate_limit_per_minute",
            "cost_per_1k_tokens",
            "total_cost",
            "tags",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "success_rate",
            "failure_rate",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "total_requests",
            "successful_requests",
            "failed_requests",
            "average_response_time",
            "total_cost",
        ]
        extra_kwargs = {"api_key": {"write_only": True}}


class LLMModelCreateSerializer(serializers.ModelSerializer):
    """LLM model creation serializer."""

    class Meta:
        model = LLMModel
        fields = [
            "name",
            "description",
            "provider",
            "model_name",
            "api_key",
            "api_base_url",
            "settings",
            "is_active",
            "is_default",
            "priority",
            "rate_limit_per_hour",
            "rate_limit_per_minute",
            "cost_per_1k_tokens",
            "tags",
        ]
        extra_kwargs = {"api_key": {"write_only": True}}


class LLMModelUpdateSerializer(serializers.ModelSerializer):
    """LLM model update serializer."""

    class Meta:
        model = LLMModel
        fields = [
            "name",
            "description",
            "model_name",
            "api_key",
            "api_base_url",
            "settings",
            "is_active",
            "is_default",
            "priority",
            "rate_limit_per_hour",
            "rate_limit_per_minute",
            "cost_per_1k_tokens",
            "tags",
        ]
        extra_kwargs = {"api_key": {"write_only": True}}


class LLMModelListSerializer(serializers.ModelSerializer):
    """LLM model list serializer."""

    created_by = UserListSerializer(read_only=True)
    success_rate = serializers.FloatField(source="get_success_rate", read_only=True)

    class Meta:
        model = LLMModel
        fields = [
            "id",
            "name",
            "description",
            "provider",
            "model_name",
            "is_active",
            "is_default",
            "priority",
            "total_requests",
            "successful_requests",
            "success_rate",
            "created_by",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "total_requests",
            "successful_requests",
        ]


class LLMModelTestSerializer(serializers.Serializer):
    """LLM model test serializer."""

    test_text = serializers.CharField(max_length=1000, required=True)
    entity_types = serializers.ListField(child=serializers.CharField(), required=False)


class LLMProcessingConfigSerializer(serializers.ModelSerializer):
    """LLM processing config serializer."""

    llm_model = LLMModelListSerializer(read_only=True)
    entity_types_display = serializers.CharField(
        source="get_entity_types_display", read_only=True
    )
    chunk_info = serializers.DictField(source="get_chunk_info", read_only=True)

    class Meta:
        model = LLMProcessingConfig
        fields = [
            "id",
            "name",
            "description",
            "llm_model",
            "chunk_size",
            "overlap_size",
            "max_tokens",
            "confidence_threshold",
            "entity_types",
            "entity_types_display",
            "prompt_type",
            "custom_prompt",
            "custom_entity_types",
            "custom_instructions",
            "enable_post_processing",
            "enable_entity_validation",
            "enable_confidence_scoring",
            "is_active",
            "chunk_info",
        ]
        read_only_fields = ["id"]


class LLMProcessingConfigCreateSerializer(serializers.ModelSerializer):
    """LLM processing config creation serializer."""

    class Meta:
        model = LLMProcessingConfig
        fields = [
            "name",
            "description",
            "llm_model",
            "chunk_size",
            "overlap_size",
            "max_tokens",
            "confidence_threshold",
            "entity_types",
            "prompt_type",
            "custom_prompt",
            "custom_entity_types",
            "custom_instructions",
            "enable_post_processing",
            "enable_entity_validation",
            "enable_confidence_scoring",
            "is_active",
        ]


class LLMProcessingConfigUpdateSerializer(serializers.ModelSerializer):
    """LLM processing config update serializer."""

    class Meta:
        model = LLMProcessingConfig
        fields = [
            "name",
            "description",
            "llm_model",
            "chunk_size",
            "overlap_size",
            "max_tokens",
            "confidence_threshold",
            "entity_types",
            "prompt_type",
            "custom_prompt",
            "custom_entity_types",
            "custom_instructions",
            "enable_post_processing",
            "enable_entity_validation",
            "enable_confidence_scoring",
            "is_active",
        ]


class LLMProcessingConfigListSerializer(serializers.ModelSerializer):
    """LLM processing config list serializer."""

    llm_model = LLMModelListSerializer(read_only=True)

    class Meta:
        model = LLMProcessingConfig
        fields = [
            "id",
            "name",
            "description",
            "llm_model",
            "prompt_type",
            "chunk_size",
            "confidence_threshold",
            "is_active",
        ]
        read_only_fields = ["id"]


class PromptTemplateSerializer(serializers.Serializer):
    """Prompt template serializer."""

    prompt_type = serializers.ChoiceField(
        choices=["general_ner", "urdu_ner", "marsiya_ner", "custom"]
    )
    text = serializers.CharField(max_length=10000)
    entity_types = serializers.ListField(child=serializers.CharField(), required=False)
    custom_prompt = serializers.CharField(required=False, allow_blank=True)
    custom_instructions = serializers.CharField(required=False, allow_blank=True)


class EntityExtractionRequestSerializer(serializers.Serializer):
    """Entity extraction request serializer."""

    text = serializers.CharField(max_length=10000, required=True)
    config_id = serializers.IntegerField(required=False)
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
    custom_instructions = serializers.CharField(required=False, allow_blank=True)


class EntityExtractionResponseSerializer(serializers.Serializer):
    """Entity extraction response serializer."""

    entities = serializers.ListField()
    processing_time = serializers.FloatField()
    tokens_used = serializers.IntegerField()
    confidence_scores = serializers.ListField()
    extraction_metadata = serializers.DictField()


class LLMProviderSerializer(serializers.Serializer):
    """LLM provider serializer."""

    name = serializers.CharField()
    provider_type = serializers.CharField()
    models = serializers.ListField()
    capabilities = serializers.ListField()
    rate_limits = serializers.DictField()
    costs = serializers.DictField()

