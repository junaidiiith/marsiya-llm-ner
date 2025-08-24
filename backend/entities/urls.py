from django.urls import path
from . import views

app_name = "entities"

urlpatterns = [
    # Entity types
    path("types/", views.EntityTypeListView.as_view(), name="entity_type_list"),
    path(
        "types/create/", views.EntityTypeCreateView.as_view(), name="entity_type_create"
    ),
    path(
        "types/<int:pk>/update/",
        views.EntityTypeUpdateView.as_view(),
        name="entity_type_update",
    ),
    # Entity management
    path(
        "list/<slug:project_slug>/<int:document_pk>/",
        views.EntityListView.as_view(),
        name="entity_list",
    ),
    path(
        "detail/<slug:project_slug>/<int:document_pk>/<int:pk>/",
        views.EntityDetailView.as_view(),
        name="entity_detail",
    ),
    path(
        "create/<slug:project_slug>/<int:document_pk>/",
        views.EntityCreateView.as_view(),
        name="entity_create",
    ),
    path(
        "update/<slug:project_slug>/<int:document_pk>/<int:pk>/",
        views.EntityUpdateView.as_view(),
        name="entity_update",
    ),
    path(
        "delete/<slug:project_slug>/<int:document_pk>/<int:pk>/",
        views.EntityDeleteView.as_view(),
        name="entity_delete",
    ),
    # Entity actions
    path(
        "verify/<slug:project_slug>/<int:document_pk>/<int:pk>/",
        views.EntityVerificationView.as_view(),
        name="entity_verify",
    ),
    path(
        "bulk-update/<slug:project_slug>/<int:document_pk>/",
        views.EntityBulkUpdateView.as_view(),
        name="entity_bulk_update",
    ),
    path(
        "bulk-verify/<slug:project_slug>/<int:document_pk>/",
        views.entity_bulk_verify,
        name="entity_bulk_verify",
    ),
    path(
        "bulk-delete/<slug:project_slug>/<int:document_pk>/",
        views.entity_bulk_delete,
        name="entity_bulk_delete",
    ),
    path(
        "stats/<slug:project_slug>/<int:document_pk>/",
        views.entity_stats,
        name="entity_stats",
    ),
    # Entity relationships
    path(
        "relationships/<slug:project_slug>/<int:document_pk>/",
        views.EntityRelationshipListView.as_view(),
        name="relationship_list",
    ),
    path(
        "relationships/create/",
        views.EntityRelationshipCreateView.as_view(),
        name="relationship_create",
    ),
    path(
        "relationships/<int:pk>/update/",
        views.EntityRelationshipUpdateView.as_view(),
        name="relationship_update",
    ),
    path(
        "relationships/<int:pk>/delete/",
        views.EntityRelationshipDeleteView.as_view(),
        name="relationship_delete",
    ),
    # Entity search
    path(
        "search/<slug:project_slug>/",
        views.EntitySearchView.as_view(),
        name="entity_search",
    ),
]
