from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer for registration and basic operations."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "bio",
            "institution",
            "academic_title",
            "research_focus",
            "research_interests",
            "is_researcher",
            "is_admin",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "password_confirm": {"write_only": True},
        }

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        """Create user with validated data."""
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer."""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "institution",
            "academic_title",
            "research_focus",
            "research_interests",
            "preferences",
            "is_researcher",
            "is_admin",
            "email_verified",
            "last_activity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "username",
            "email_verified",
            "created_at",
            "updated_at",
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """User profile update serializer."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "bio",
            "institution",
            "academic_title",
            "research_focus",
            "research_interests",
            "preferences",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer."""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError("New passwords don't match")
        return attrs

    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """Reset password serializer."""

    email = serializers.EmailField(required=True)


class ResetPasswordConfirmSerializer(serializers.Serializer):
    """Reset password confirm serializer."""

    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    """User list serializer for public views."""

    full_name = serializers.SerializerMethodField()
    profile_completion = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "full_name",
            "institution",
            "academic_title",
            "research_focus",
            "profile_completion",
            "created_at",
        ]
        read_only_fields = ["id", "username", "created_at"]

    def get_full_name(self, obj):
        """Get user's full name."""
        return obj.get_full_name()

    def get_profile_completion(self, obj):
        """Get profile completion percentage."""
        try:
            return obj.profile.profile_completion
        except UserProfile.DoesNotExist:
            return 0
