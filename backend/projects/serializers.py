from rest_framework import serializers
from .models import Project, ProjectMembership
from users.serializers import UserListSerializer


class ProjectMembershipSerializer(serializers.ModelSerializer):
    """Project membership serializer."""

    user = UserListSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    permissions_display = serializers.CharField(
        source="get_permissions_display", read_only=True
    )

    class Meta:
        model = ProjectMembership
        fields = [
            "id",
            "user",
            "user_id",
            "role",
            "can_edit_project",
            "can_manage_members",
            "can_upload_documents",
            "can_edit_entities",
            "can_export_data",
            "joined_at",
            "is_active",
            "notes",
            "permissions_display",
        ]
        read_only_fields = ["id", "joined_at"]


class ProjectSerializer(serializers.ModelSerializer):
    """Project serializer."""

    created_by = UserListSerializer(read_only=True)
    members_count = serializers.IntegerField(source="get_members_count", read_only=True)
    documents_count = serializers.IntegerField(
        source="get_documents_count", read_only=True
    )
    entities_count = serializers.IntegerField(
        source="get_entities_count", read_only=True
    )
    verified_entities_count = serializers.IntegerField(
        source="get_verified_entities_count", read_only=True
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "slug",
            "research_area",
            "methodology",
            "objectives",
            "timeline",
            "status",
            "is_public",
            "allow_public_view",
            "tags",
            "references",
            "created_by",
            "created_at",
            "updated_at",
            "members_count",
            "documents_count",
            "entities_count",
            "verified_entities_count",
        ]
        read_only_fields = ["id", "slug", "created_by", "created_at", "updated_at"]


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Project creation serializer."""

    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "research_area",
            "methodology",
            "objectives",
            "timeline",
            "status",
            "is_public",
            "allow_public_view",
            "tags",
            "references",
        ]


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """Project update serializer."""

    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "research_area",
            "methodology",
            "objectives",
            "timeline",
            "status",
            "is_public",
            "allow_public_view",
            "tags",
            "references",
        ]
        extra_kwargs = {
            "name": {"required": False},
            "description": {"required": False},
            "research_area": {"required": False},
            "methodology": {"required": False},
            "objectives": {"required": False},
            "timeline": {"required": False},
            "status": {"required": False},
            "is_public": {"required": False},
            "allow_public_view": {"required": False},
            "tags": {"required": False},
            "references": {"required": False},
        }


class ProjectDetailSerializer(ProjectSerializer):
    """Project detail serializer with members."""

    members = ProjectMembershipSerializer(
        source="memberships", many=True, read_only=True
    )

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ["members"]


class ProjectListSerializer(serializers.ModelSerializer):
    """Project list serializer."""

    created_by = UserListSerializer(read_only=True)
    members_count = serializers.IntegerField(source="get_members_count", read_only=True)
    documents_count = serializers.IntegerField(
        source="get_documents_count", read_only=True
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "slug",
            "research_area",
            "status",
            "is_public",
            "created_by",
            "created_at",
            "members_count",
            "documents_count",
        ]
        read_only_fields = ["id", "slug", "created_by", "created_at"]


class ProjectMembershipCreateSerializer(serializers.ModelSerializer):
    """Project membership creation serializer."""

    class Meta:
        model = ProjectMembership
        fields = ["user", "role", "notes"]

    def validate(self, attrs):
        """Validate membership creation."""
        user = attrs["user"]
        project = self.context["project"]

        # Check if user is already a member
        if ProjectMembership.objects.filter(user=user, project=project).exists():
            raise serializers.ValidationError(
                "User is already a member of this project"
            )

        return attrs


class ProjectMembershipUpdateSerializer(serializers.ModelSerializer):
    """Project membership update serializer."""

    class Meta:
        model = ProjectMembership
        fields = [
            "role",
            "can_edit_project",
            "can_manage_members",
            "can_upload_documents",
            "can_edit_entities",
            "can_export_data",
            "is_active",
            "notes",
        ]


class ProjectStatsSerializer(serializers.Serializer):
    """Project statistics serializer."""

    total_documents = serializers.IntegerField()
    total_entities = serializers.IntegerField()
    verified_entities = serializers.IntegerField()
    unverified_entities = serializers.IntegerField()
    entity_types_breakdown = serializers.DictField()
    verification_rate = serializers.FloatField()
    recent_activity = serializers.ListField()
