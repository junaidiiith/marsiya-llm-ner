from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    ResetPasswordConfirmSerializer,
    UserListSerializer,
)
from .models import UserProfile

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """User registration view."""

    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create user profile
        UserProfile.objects.create(user=user)

        return Response(
            {"message": "User registered successfully", "user_id": user.id},
            status=status.HTTP_201_CREATED,
        )


class UserProfileView(generics.RetrieveAPIView):
    """User profile view."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    """User profile update view."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileUpdateSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Update user profile completion
        if hasattr(user, "profile"):
            user.profile.calculate_profile_completion()

        serializer.save()
        return Response(
            {
                "message": "Profile updated successfully",
                "user": UserProfileSerializer(user).data,
            }
        )


class ChangePasswordView(generics.UpdateAPIView):
    """Change password view."""

    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Change password
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        # Update session
        update_session_auth_hash(request, user)

        return Response({"message": "Password changed successfully"})


class ResetPasswordView(generics.GenericAPIView):
    """Reset password view."""

    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            # In a real implementation, you would send a reset email here
            # For now, we'll just return a success message
            return Response({"message": "Password reset email sent successfully"})
        except User.DoesNotExist:
            return Response({"message": "Password reset email sent successfully"})


class ResetPasswordConfirmView(generics.GenericAPIView):
    """Reset password confirm view."""

    permission_classes = [AllowAny]
    serializer_class = ResetPasswordConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # In a real implementation, you would validate the token here
        # For now, we'll just return a success message
        return Response({"message": "Password reset successfully"})


class UserListView(generics.ListAPIView):
    """User list view for public profiles."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserListSerializer
    queryset = User.objects.filter(is_active=True)

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by research interests
        research_focus = self.request.query_params.get("research_focus")
        if research_focus:
            queryset = queryset.filter(research_focus__icontains=research_focus)

        # Filter by institution
        institution = self.request.query_params.get("institution")
        if institution:
            queryset = queryset.filter(institution__icontains=institution)

        # Filter by academic title
        academic_title = self.request.query_params.get("academic_title")
        if academic_title:
            queryset = queryset.filter(academic_title__icontains=academic_title)

        return queryset


class UserDetailView(generics.RetrieveAPIView):
    """User detail view for public profiles."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserListSerializer
    queryset = User.objects.filter(is_active=True)
    lookup_field = "username"


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_last_activity(request):
    """Update user's last activity."""
    user = request.user
    user.update_last_activity()
    return Response({"message": "Activity updated"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_stats(request):
    """Get user statistics."""
    user = request.user

    # Get user's projects count
    projects_count = user.projects.count()

    # Get user's documents count
    documents_count = user.documents.count()

    # Get user's entities count
    entities_count = user.entities.count()

    # Get user's verified entities count
    verified_entities_count = user.verified_entities.count()

    return Response(
        {
            "projects_count": projects_count,
            "documents_count": documents_count,
            "entities_count": entities_count,
            "verified_entities_count": verified_entities_count,
            "profile_completion": getattr(user.profile, "profile_completion", 0)
            if hasattr(user, "profile")
            else 0,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_preferences(request):
    """Update user preferences."""
    user = request.user
    preferences = request.data.get("preferences", {})

    if not isinstance(preferences, dict):
        return Response(
            {"error": "Preferences must be a dictionary"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Update preferences
    for key, value in preferences.items():
        user.set_preference(key, value)

    return Response(
        {"message": "Preferences updated successfully", "preferences": user.preferences}
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_preferences(request):
    """Get user preferences."""
    user = request.user
    key = request.query_params.get("key")

    if key:
        value = user.get_preference(key)
        return Response({key: value})

    return Response(user.preferences)
