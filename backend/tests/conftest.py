"""
Pytest configuration and fixtures for Marsiya LLM NER backend tests.
"""

import pytest
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "marsiya_ner.settings")
django.setup()

# Now import Django modules after setup
from django.conf import settings
from django.test import RequestFactory
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from users.models import UserProfile
from projects.models import Project, ProjectMembership
from documents.models import Document, DocumentVersion
from entities.models import EntityType, Entity
from llm_integration.models import LLMModel, LLMProcessingConfig
from processing.models import ProcessingJob
from core.models import AuditLog

User = get_user_model()


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up the test database."""
    with django_db_blocker.unblock():
        # Create initial data
        create_test_data()


@pytest.fixture
def api_client():
    """Return an API client instance."""
    return APIClient()


@pytest.fixture
def request_factory():
    """Return a request factory instance."""
    return RequestFactory()


@pytest.fixture
def test_user():
    """Create and return a test user."""
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )
    UserProfile.objects.create(
        user=user,
        research_interests="Digital Humanities, Urdu Literature",
        institution="Test University",
        role="Researcher",
    )
    return user


@pytest.fixture
def test_user2():
    """Create and return a second test user."""
    user = User.objects.create_user(
        username="testuser2",
        email="test2@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User2",
    )
    UserProfile.objects.create(
        user=user,
        research_interests="Islamic Studies, Poetry",
        institution="Test University",
        role="Student",
    )
    return user


@pytest.fixture
def admin_user():
    """Create and return an admin user."""
    user = User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
        is_staff=True,
        is_superuser=True,
    )
    UserProfile.objects.create(
        user=user,
        research_interests="System Administration",
        institution="Test University",
        role="Administrator",
    )
    return user


@pytest.fixture
def test_project(test_user):
    """Create and return a test project."""
    project = Project.objects.create(
        title="Test Marsiya Project",
        description="A test project for Marsiya poetry analysis",
        slug="test-marsiya-project",
        created_by=test_user,
        is_public=False,
    )
    ProjectMembership.objects.create(project=project, user=test_user, role="owner")
    return project


@pytest.fixture
def test_project2(test_user2):
    """Create and return a second test project."""
    project = Project.objects.create(
        title="Test Project 2",
        description="Another test project",
        slug="test-project-2",
        created_by=test_user2,
        is_public=True,
    )
    ProjectMembership.objects.create(project=project, user=test_user2, role="owner")
    return project


@pytest.fixture
def test_document(test_project, test_user):
    """Create and return a test document."""
    document = Document.objects.create(
        title="Test Marsiya Text",
        content="This is a test Marsiya text for entity extraction.",
        language="urdu",
        project=test_project,
        created_by=test_user,
        processing_status="pending",
    )
    DocumentVersion.objects.create(
        document=document,
        version_number=1,
        content=document.content,
        changed_by=test_user,
    )
    return document


@pytest.fixture
def test_entity_types():
    """Create and return test entity types."""
    entity_types = []
    type_data = [
        ("PERSON", "Names of people, prophets, Imams"),
        ("LOCATION", "Places, landmarks, geographical features"),
        ("DATE", "Dates, Islamic months, specific days"),
        ("TIME", "Time references and periods"),
        ("ORGANIZATION", "Groups, tribes, armies, institutions"),
        ("DESIGNATION", "Titles, honorifics, roles"),
        ("NUMBER", "Numerically significant values"),
    ]

    for name, description in type_data:
        entity_type, _ = EntityType.objects.get_or_create(
            name=name,
            defaults={
                "description": description,
                "color_code": f"#{hash(name) % 0xFFFFFF:06x}",
                "is_active": True,
            },
        )
        entity_types.append(entity_type)

    return entity_types


@pytest.fixture
def test_llm_model():
    """Create and return a test LLM model."""
    model = LLMModel.objects.create(
        name="Test GPT Model",
        description="A test model for development",
        provider="openai",
        model_name="gpt-3.5-turbo",
        api_key="test-key-123",
        is_active=True,
        cost_per_1k_tokens=0.002,
    )
    return model


@pytest.fixture
def test_llm_config(test_llm_model):
    """Create and return a test LLM processing configuration."""
    config = LLMProcessingConfig.objects.create(
        name="Test Marsiya Config",
        llm_model=test_llm_model,
        prompt_type="marsiya_ner",
        max_tokens=2000,
        chunk_size=1000,
        overlap_size=100,
        confidence_threshold=0.7,
        is_active=True,
    )
    return config


@pytest.fixture
def test_entity(test_document, test_entity_types):
    """Create and return a test entity."""
    entity = Entity.objects.create(
        document=test_document,
        text="Test Entity",
        entity_type=test_entity_types[0],  # PERSON
        start_position=0,
        end_position=11,
        confidence=0.9,
        source="manual",
        is_verified=True,
    )
    return entity


@pytest.fixture
def test_processing_job(test_document, test_user):
    """Create and return a test processing job."""
    job = ProcessingJob.objects.create(
        document=test_document,
        job_type="entity_extraction",
        status="pending",
        progress=0,
        created_by=test_user,
        metadata={"prompt_type": "marsiya", "text_length": len(test_document.content)},
    )
    return job


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Return an authenticated API client."""
    refresh = RefreshToken.for_user(test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Return an admin API client."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


def create_test_data():
    """Create initial test data."""
    # This function will be called during test setup
    pass


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass
