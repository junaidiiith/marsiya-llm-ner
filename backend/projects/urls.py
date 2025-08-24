from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    # Project management
    path("create/", views.ProjectCreateView.as_view(), name="project_create"),
    path("list/", views.ProjectListView.as_view(), name="project_list"),
    path(
        "detail/<slug:slug>/", views.ProjectDetailView.as_view(), name="project_detail"
    ),
    path(
        "update/<slug:slug>/", views.ProjectUpdateView.as_view(), name="project_update"
    ),
    path(
        "delete/<slug:slug>/", views.ProjectDeleteView.as_view(), name="project_delete"
    ),
    # Project actions
    path("archive/<slug:slug>/", views.project_archive, name="project_archive"),
    path("restore/<slug:slug>/", views.project_restore, name="project_restore"),
    path("stats/<slug:slug>/", views.project_stats, name="project_stats"),
    path("user-projects/", views.user_projects, name="user_projects"),
    # Project membership
    path(
        "<slug:project_slug>/members/",
        views.ProjectMembershipListView.as_view(),
        name="membership_list",
    ),
    path(
        "<slug:project_slug>/members/create/",
        views.ProjectMembershipCreateView.as_view(),
        name="membership_create",
    ),
    path(
        "<slug:project_slug>/members/<int:pk>/update/",
        views.ProjectMembershipUpdateView.as_view(),
        name="membership_update",
    ),
    path(
        "<slug:project_slug>/members/<int:pk>/delete/",
        views.ProjectMembershipDeleteView.as_view(),
        name="membership_delete",
    ),
]
