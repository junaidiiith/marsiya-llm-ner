from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    # Audit logs
    path("audit-logs/", views.AuditLogListView.as_view(), name="audit_log_list"),
    path(
        "audit-logs/<int:pk>/",
        views.AuditLogDetailView.as_view(),
        name="audit_log_detail",
    ),
    path(
        "audit-logs/filter/",
        views.AuditLogFilterView.as_view(),
        name="audit_log_filter",
    ),
    path("audit-logs/stats/", views.audit_log_stats, name="audit_log_stats"),
    # System administration
    path("system/health/", views.system_health, name="system_health"),
    path("system/info/", views.system_info, name="system_info"),
    path("system/database-stats/", views.database_stats, name="database_stats"),
    path("system/clear-cache/", views.clear_cache, name="clear_cache"),
    path(
        "system/user-activity/",
        views.user_activity_summary,
        name="user_activity_summary",
    ),
    # Data management
    path("export/", views.export_request, name="export_request"),
    path("import/", views.import_request, name="import_request"),
]
