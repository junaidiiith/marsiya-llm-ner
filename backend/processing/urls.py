from django.urls import path
from . import views

app_name = "processing"

urlpatterns = [
    # Processing jobs
    path("jobs/", views.ProcessingJobListView.as_view(), name="job_list"),
    path("jobs/create/", views.ProcessingJobCreateView.as_view(), name="job_create"),
    path("jobs/<int:pk>/", views.ProcessingJobDetailView.as_view(), name="job_detail"),
    path(
        "jobs/<int:pk>/update/",
        views.ProcessingJobUpdateView.as_view(),
        name="job_update",
    ),
    path(
        "jobs/<int:pk>/delete/",
        views.ProcessingJobDeleteView.as_view(),
        name="job_delete",
    ),
    # Job actions
    path(
        "jobs/<int:pk>/progress/",
        views.ProcessingJobProgressView.as_view(),
        name="job_progress",
    ),
    path(
        "jobs/<int:pk>/result/",
        views.ProcessingJobResultView.as_view(),
        name="job_result",
    ),
    path(
        "jobs/<int:pk>/action/",
        views.ProcessingJobActionView.as_view(),
        name="job_action",
    ),
    # Job filtering and statistics
    path("jobs/filter/", views.ProcessingJobFilterView.as_view(), name="job_filter"),
    path("jobs/stats/", views.processing_job_stats, name="job_stats"),
    path("jobs/bulk-action/", views.processing_job_bulk_action, name="job_bulk_action"),
    path("jobs/queue-status/", views.processing_queue_status, name="queue_status"),
    # Project-specific processing
    path(
        "projects/<slug:project_slug>/stats/",
        views.project_processing_stats,
        name="project_processing_stats",
    ),
]
