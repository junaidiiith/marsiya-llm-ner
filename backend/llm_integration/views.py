from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from .models import LLMModel, LLMProcessingConfig
from .serializers import (
    LLMModelSerializer,
    LLMModelCreateSerializer,
    LLMModelUpdateSerializer,
    LLMModelListSerializer,
    LLMModelTestSerializer,
    LLMProcessingConfigSerializer,
    LLMProcessingConfigCreateSerializer,
    LLMProcessingConfigUpdateSerializer,
    LLMProcessingConfigListSerializer,
    PromptTemplateSerializer,
    EntityExtractionRequestSerializer,
    EntityExtractionResponseSerializer,
    LLMProviderSerializer,
)
from .services import LLMService
from .tasks import test_llm_connection


class LLMModelListView(generics.ListAPIView):
    """List all LLM models."""

    permission_classes = [IsAuthenticated]
    serializer_class = LLMModelListSerializer
    queryset = LLMModel.objects.filter(is_active=True).order_by("priority", "name")

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by provider
        provider = self.request.query_params.get("provider")
        if provider:
            queryset = queryset.filter(provider=provider)

        # Filter by active status
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            is_active_bool = is_active.lower() == "true"
            queryset = queryset.filter(is_active=is_active_bool)

        # Filter by default status
        is_default = self.request.query_params.get("is_default")
        if is_default is not None:
            is_default_bool = is_default.lower() == "true"
            queryset = queryset.filter(is_default=is_default_bool)

        return queryset


class LLMModelCreateView(generics.CreateAPIView):
    """Create a new LLM model."""

    permission_classes = [IsAuthenticated]
    serializer_class = LLMModelCreateSerializer

    def perform_create(self, serializer):
        # If this is the first model, make it default
        if not LLMModel.objects.exists():
            serializer.save(created_by=self.request.user, is_default=True)
        else:
            serializer.save(created_by=self.request.user)


class LLMModelDetailView(generics.RetrieveAPIView):
    """Get LLM model details."""

    permission_classes = [IsAuthenticated]
    serializer_class = LLMModelSerializer
    queryset = LLMModel.objects.all()


class LLMModelUpdateView(generics.UpdateAPIView):
    """Update an LLM model."""

    permission_classes = [IsAuthenticated]
    serializer_class = LLMModelUpdateSerializer
    queryset = LLMModel.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class LLMModelDeleteView(generics.DestroyAPIView):
    """Delete an LLM model."""

    permission_classes = [IsAuthenticated]
    queryset = LLMModel.objects.all()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()


class LLMModelTestView(generics.GenericAPIView):
    """Test LLM model connection."""

    permission_classes = [IsAuthenticated]
    serializer_class = LLMModelTestSerializer

    def post(self, request, pk):
        llm_model = get_object_or_404(LLMModel, pk=pk)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Start async test
        task = test_llm_connection.delay(llm_model_id=llm_model.id)

        return Response(
            {
                "message": "LLM connection test started successfully",
                "llm_model_id": llm_model.id,
                "task_id": task.id,
            }
        )


class LLMProcessingConfigListView(generics.ListAPIView):
    """List LLM processing configurations."""

    permission_classes = [IsAuthenticated]
    serializer_class = LLMProcessingConfigListSerializer
    queryset = LLMProcessingConfig.objects.filter(is_active=True).order_by("name")

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by LLM model
        llm_model = self.request.query_params.get("llm_model")
        if llm_model:
            queryset = queryset.filter(llm_model_id=llm_model)

        # Filter by prompt type
        prompt_type = self.request.query_params.get("prompt_type")
        if prompt_type:
            queryset = queryset.filter(prompt_type=prompt_type)

        # Filter by active status
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            is_active_bool = is_active.lower() == "true"
            queryset = queryset.filter(is_active=is_active_bool)

        return queryset


class LLMProcessingConfigCreateView(generics.CreateAPIView):
    """Create a new LLM processing configuration."""

    permission_classes = [IsAuthenticated]
    serializer_class = LLMProcessingConfigCreateSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class LLMProcessingConfigDetailView(generics.RetrieveAPIView):
    """Get LLM processing configuration details."""

    permission_classes = [IsAuthenticated]
    serializer_class = LLMProcessingConfigSerializer
    queryset = LLMProcessingConfig.objects.all()


class LLMProcessingConfigUpdateView(generics.UpdateAPIView):
    """Update an LLM processing configuration."""

    permission_classes = [IsAuthenticated]
    serializer_class = LLMProcessingConfigUpdateSerializer
    queryset = LLMProcessingConfig.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class LLMProcessingConfigDeleteView(generics.DestroyAPIView):
    """Delete an LLM processing configuration."""

    permission_classes = [IsAuthenticated]
    queryset = LLMProcessingConfig.objects.all()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()


class EntityExtractionView(generics.GenericAPIView):
    """Extract entities from text using LLM."""

    permission_classes = [IsAuthenticated]
    serializer_class = EntityExtractionRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        text = serializer.validated_data["text"]
        llm_config_id = serializer.validated_data.get("llm_config_id")
        prompt_type = serializer.validated_data.get("prompt_type", "marsiya_ner")
        custom_prompt = serializer.validated_data.get("custom_prompt")
        custom_entity_types = serializer.validated_data.get("custom_entity_types", [])

        try:
            # Get LLM configuration
            if llm_config_id:
                llm_config = get_object_or_404(LLMProcessingConfig, id=llm_config_id)
            else:
                # Get default configuration
                llm_config = LLMProcessingConfig.objects.filter(
                    is_active=True, prompt_type=prompt_type
                ).first()

                if not llm_config:
                    return Response(
                        {
                            "error": f"No active configuration found for prompt type: {prompt_type}"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Initialize LLM service
            llm_service = LLMService()

            # Extract entities
            entities = llm_service.extract_entities(text=text, prompt_type=prompt_type)

            # Serialize response
            response_data = {
                "entities": entities,
                "total_entities": len(entities),
                "llm_config_used": {
                    "id": llm_config.id,
                    "name": llm_config.name,
                    "prompt_type": llm_config.prompt_type,
                },
                "processing_time": entities[0].get("processing_time")
                if entities
                else None,
                "tokens_used": len(entities),  # Simplified token count
            }

            response_serializer = EntityExtractionResponseSerializer(response_data)
            return Response(response_serializer.data)

        except Exception as e:
            return Response(
                {"error": f"Entity extraction failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def prompt_templates(request):
    """Get available prompt templates."""
    templates = {
        "general_ner": {
            "name": "General NER",
            "description": "Generic named entity recognition without domain-specific knowledge",
            "entity_types": [
                "PERSON",
                "LOCATION",
                "DATE",
                "TIME",
                "ORGANIZATION",
                "DESIGNATION",
                "NUMBER",
            ],
            "example": "Extract named entities from the given text in a generic way.",
        },
        "urdu_ner": {
            "name": "Urdu NER",
            "description": "Urdu-specific named entity recognition with linguistic and cultural knowledge",
            "entity_types": [
                "PERSON",
                "LOCATION",
                "DATE",
                "TIME",
                "ORGANIZATION",
                "DESIGNATION",
                "NUMBER",
            ],
            "example": "Extract named entities from Urdu text considering Urdu-specific linguistic and cultural nuances.",
        },
        "marsiya_ner": {
            "name": "Marsiya NER",
            "description": "Marsiya-specific named entity recognition with deep domain knowledge",
            "entity_types": [
                "PERSON",
                "LOCATION",
                "DATE",
                "TIME",
                "ORGANIZATION",
                "DESIGNATION",
                "NUMBER",
            ],
            "example": "Extract named entities from Urdu Marsiya text applying deep domain-specific knowledge.",
        },
        "custom": {
            "name": "Custom Prompt",
            "description": "User-defined custom prompt and entity types",
            "entity_types": "User-defined",
            "example": "Define your own prompt and entity types for specialized NER tasks.",
        },
    }

    serializer = PromptTemplateSerializer(templates, many=False)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def llm_providers(request):
    """Get available LLM providers."""
    providers = {
        "openai": {
            "name": "OpenAI",
            "description": "OpenAI GPT models including GPT-4 and GPT-3.5",
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "features": ["High accuracy", "Fast processing", "Multiple languages"],
            "pricing": "Per token pricing",
        },
        "anthropic": {
            "name": "Anthropic",
            "description": "Anthropic Claude models with strong reasoning capabilities",
            "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "features": ["Strong reasoning", "Safety-focused", "Context understanding"],
            "pricing": "Per token pricing",
        },
        "local": {
            "name": "Local Models",
            "description": "Locally hosted open-source models",
            "models": ["llama-2", "mistral", "codellama"],
            "features": ["Privacy", "No API costs", "Customizable"],
            "pricing": "One-time setup cost",
        },
        "custom": {
            "name": "Custom API",
            "description": "Custom API endpoints for specialized models",
            "models": "User-defined",
            "features": ["Custom integration", "Specialized models", "Flexible"],
            "pricing": "Varies",
        },
    }

    serializer = LLMProviderSerializer(providers, many=False)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def llm_stats(request):
    """Get LLM usage statistics."""
    # Get total requests across all models
    total_requests = (
        LLMModel.objects.aggregate(total=Count("total_requests"))["total"] or 0
    )

    successful_requests = (
        LLMModel.objects.aggregate(successful=Count("successful_requests"))[
            "successful"
        ]
        or 0
    )

    failed_requests = (
        LLMModel.objects.aggregate(failed=Count("failed_requests"))["failed"] or 0
    )

    # Get average response times
    avg_response_time = LLMModel.objects.aggregate(
        avg_time=Avg("average_response_time")
    )["avg_time"]

    # Get total cost
    total_cost = LLMModel.objects.aggregate(cost=Sum("total_cost"))["cost"] or 0

    # Get provider distribution
    provider_stats = (
        LLMModel.objects.values("provider")
        .annotate(
            count=Count("id"),
            total_requests=Sum("total_requests"),
            successful_requests=Sum("successful_requests"),
        )
        .order_by("-total_requests")
    )

    stats = {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "success_rate": (successful_requests / total_requests * 100)
        if total_requests > 0
        else 0,
        "average_response_time": avg_response_time,
        "total_cost": total_cost,
        "provider_distribution": list(provider_stats),
        "active_models": LLMModel.objects.filter(is_active=True).count(),
        "total_models": LLMModel.objects.count(),
    }

    return Response(stats)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def set_default_llm_model(request, pk):
    """Set an LLM model as default."""
    llm_model = get_object_or_404(LLMModel, pk=pk)

    # Remove default from other models
    LLMModel.objects.filter(is_default=True).update(is_default=False)

    # Set this model as default
    llm_model.is_default = True
    llm_model.save()

    return Response({"message": f"{llm_model.name} set as default LLM model"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reset_llm_stats(request, pk):
    """Reset LLM model statistics."""
    llm_model = get_object_or_404(LLMModel, pk=pk)

    llm_model.total_requests = 0
    llm_model.successful_requests = 0
    llm_model.failed_requests = 0
    llm_model.average_response_time = None
    llm_model.total_cost = 0
    llm_model.save()

    return Response({"message": f"Statistics reset for {llm_model.name}"})
