from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    # Authentication
    path("register/", views.UserRegistrationView.as_view(), name="user_register"),
    path("profile/", views.UserProfileView.as_view(), name="user_profile"),
    path(
        "profile/update/",
        views.UserProfileUpdateView.as_view(),
        name="user_profile_update",
    ),
    path(
        "change-password/", views.ChangePasswordView.as_view(), name="change_password"
    ),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset_password"),
    path(
        "reset-password/confirm/",
        views.ResetPasswordConfirmView.as_view(),
        name="reset_password_confirm",
    ),
    # User management
    path("list/", views.UserListView.as_view(), name="user_list"),
    path("detail/<str:username>/", views.UserDetailView.as_view(), name="user_detail"),
    # User actions
    path("update-activity/", views.update_last_activity, name="update_activity"),
    path("stats/", views.user_stats, name="user_stats"),
    path("preferences/", views.get_preferences, name="get_preferences"),
    path("preferences/update/", views.update_preferences, name="update_preferences"),
]
