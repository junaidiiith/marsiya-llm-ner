from django.urls import path
from . import views

app_name = "llm_integration"

urlpatterns = [
    # LLM models
    path("models/", views.LLMModelListView.as_view(), name="llm_model_list"),
    path("models/create/", views.LLMModelCreateView.as_view(), name="llm_model_create"),
    path(
        "models/<int:pk>/", views.LLMModelDetailView.as_view(), name="llm_model_detail"
    ),
    path(
        "models/<int:pk>/update/",
        views.LLMModelUpdateView.as_view(),
        name="llm_model_update",
    ),
    path(
        "models/<int:pk>/delete/",
        views.LLMModelDeleteView.as_view(),
        name="llm_model_delete",
    ),
    path(
        "models/<int:pk>/test/", views.LLMModelTestView.as_view(), name="llm_model_test"
    ),
    # LLM processing configurations
    path("configs/", views.LLMProcessingConfigListView.as_view(), name="config_list"),
    path(
        "configs/create/",
        views.LLMProcessingConfigCreateView.as_view(),
        name="config_create",
    ),
    path(
        "configs/<int:pk>/",
        views.LLMProcessingConfigDetailView.as_view(),
        name="config_detail",
    ),
    path(
        "configs/<int:pk>/update/",
        views.LLMProcessingConfigUpdateView.as_view(),
        name="config_update",
    ),
    path(
        "configs/<int:pk>/delete/",
        views.LLMProcessingConfigDeleteView.as_view(),
        name="config_delete",
    ),
    # Entity extraction
    path("extract/", views.EntityExtractionView.as_view(), name="entity_extraction"),
    # System information
    path("prompt-templates/", views.prompt_templates, name="prompt_templates"),
    path("providers/", views.llm_providers, name="llm_providers"),
    path("stats/", views.llm_stats, name="llm_stats"),
    # LLM model actions
    path(
        "models/<int:pk>/set-default/",
        views.set_default_llm_model,
        name="set_default_model",
    ),
    path(
        "models/<int:pk>/reset-stats/", views.reset_llm_stats, name="reset_model_stats"
    ),
]
