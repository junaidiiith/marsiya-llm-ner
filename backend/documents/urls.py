from django.urls import path
from . import views

app_name = "documents"

urlpatterns = [
    # Document management
    path("create/", views.DocumentCreateView.as_view(), name="document_create"),
    path("upload/", views.DocumentUploadView.as_view(), name="document_upload"),
    path(
        "list/<slug:project_slug>/",
        views.DocumentListView.as_view(),
        name="document_list",
    ),
    path(
        "detail/<slug:project_slug>/<int:pk>/",
        views.DocumentDetailView.as_view(),
        name="document_detail",
    ),
    path(
        "update/<slug:project_slug>/<int:pk>/",
        views.DocumentUpdateView.as_view(),
        name="document_update",
    ),
    path(
        "delete/<slug:project_slug>/<int:pk>/",
        views.DocumentDeleteView.as_view(),
        name="document_delete",
    ),
    # Document actions
    path(
        "process/<slug:project_slug>/<int:pk>/",
        views.DocumentProcessingView.as_view(),
        name="document_process",
    ),
    path(
        "restore/<slug:project_slug>/<int:pk>/",
        views.document_restore,
        name="document_restore",
    ),
    path(
        "stats/<slug:project_slug>/<int:pk>/",
        views.document_stats,
        name="document_stats",
    ),
    path("search/<slug:project_slug>/", views.document_search, name="document_search"),
    path(
        "bulk-action/<slug:project_slug>/",
        views.document_bulk_action,
        name="document_bulk_action",
    ),
    # Document versions
    path(
        "<slug:project_slug>/<int:document_pk>/versions/",
        views.DocumentVersionListView.as_view(),
        name="version_list",
    ),
    path(
        "<slug:project_slug>/<int:document_pk>/versions/<int:pk>/",
        views.DocumentVersionDetailView.as_view(),
        name="version_detail",
    ),
]
