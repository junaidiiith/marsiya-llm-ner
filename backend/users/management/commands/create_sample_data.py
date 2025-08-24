from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import Project
from processing.models import ProcessingJob
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = "Create sample data for testing the frontend"

    def handle(self, *args, **options):
        self.stdout.write("Creating sample data...")

        # Get or create a test user
        user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "first_name": "Admin",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password("admin123")
            user.save()
            self.stdout.write(f"Created user: {user.username}")
        else:
            self.stdout.write(f"Using existing user: {user.username}")

        # Create sample projects
        self.create_sample_projects(user)

        # Create sample processing jobs
        self.create_sample_processing_jobs(user)

        self.stdout.write(
            self.style.SUCCESS("Sample data creation completed successfully!")
        )

    def create_sample_projects(self, user):
        """Create sample projects."""
        projects_data = [
            {
                "name": "Marsiya Analysis Project",
                "description": "A comprehensive analysis of Marsiya poetry for entity recognition",
                "status": "active",
                "research_area": "Islamic Literature",
                "objectives": [
                    "Extract named entities from Marsiya texts",
                    "Analyze historical references",
                    "Create entity database",
                ],
                "timeline": {"start_date": "2024-01-01", "end_date": "2024-12-31"},
                "tags": ["marsiya", "poetry", "ner", "islamic-literature"],
            },
            {
                "name": "Historical Documents Project",
                "description": "Processing historical Islamic documents for entity extraction",
                "status": "active",
                "research_area": "Islamic History",
                "objectives": [
                    "Process historical documents",
                    "Extract historical entities",
                    "Build timeline database",
                ],
                "timeline": {"start_date": "2024-02-01", "end_date": "2024-11-30"},
                "tags": ["historical", "documents", "islamic-history"],
            },
            {
                "name": "Quranic Text Analysis",
                "description": "Entity recognition in Quranic texts and commentaries",
                "status": "planning",
                "research_area": "Religious Studies",
                "objectives": [
                    "Analyze Quranic texts",
                    "Extract religious entities",
                    "Study commentaries",
                ],
                "timeline": {"start_date": "2024-03-01", "end_date": "2024-10-31"},
                "tags": ["quran", "religious-texts", "commentary"],
            },
        ]

        created_count = 0
        for data in projects_data:
            project, created = Project.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "status": data["status"],
                    "research_area": data["research_area"],
                    "objectives": data["objectives"],
                    "timeline": data["timeline"],
                    "tags": data["tags"],
                    "created_by": user,
                    "updated_by": user,
                },
            )
            if created:
                # Add user as project member
                project.add_member(user, "owner")
                created_count += 1
                self.stdout.write(f"Created project: {project.name}")

        self.stdout.write(f"Created {created_count} projects")

    def create_sample_processing_jobs(self, user):
        """Create sample processing jobs."""
        jobs_data = [
            {
                "name": "Annual Report Processing",
                "description": "Processing annual financial reports for entity extraction",
                "job_type": "ner_processing",
                "status": "running",
                "progress": 65,
                "priority": 8,
                "total_steps": 10,
                "current_step": "Entity extraction in progress",
            },
            {
                "name": "Technical Documentation Analysis",
                "description": "Analyzing technical specifications for named entities",
                "job_type": "document_analysis",
                "status": "queued",
                "progress": 0,
                "priority": 5,
                "total_steps": 8,
                "current_step": "Waiting in queue",
            },
            {
                "name": "Financial Reports Q4",
                "description": "Processing Q4 financial reports for entity recognition",
                "job_type": "ner_processing",
                "status": "completed",
                "progress": 100,
                "priority": 9,
                "total_steps": 12,
                "current_step": "Completed successfully",
            },
            {
                "name": "Customer Feedback Analysis",
                "description": "Extracting entities from customer feedback documents",
                "job_type": "entity_verification",
                "status": "failed",
                "progress": 23,
                "priority": 3,
                "total_steps": 6,
                "current_step": "Failed during processing",
                "error_message": "Model timeout after 2 hours of processing",
            },
        ]

        created_count = 0
        for data in jobs_data:
            # Get a project for the job
            project = Project.objects.first()

            job, created = ProcessingJob.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "job_type": data["job_type"],
                    "status": data["status"],
                    "progress": data["progress"],
                    "priority": data["priority"],
                    "total_steps": data["total_steps"],
                    "current_step": data["current_step"],
                    "project": project,
                    "created_by": user,
                    "updated_by": user,
                },
            )

            if created:
                # Set timing information based on status
                if data["status"] == "running":
                    job.started_at = timezone.now() - timedelta(hours=1)
                elif data["status"] == "completed":
                    job.started_at = timezone.now() - timedelta(hours=3)
                    job.completed_at = timezone.now() - timedelta(hours=1)
                elif data["status"] == "failed":
                    job.started_at = timezone.now() - timedelta(hours=4)
                    job.completed_at = timezone.now() - timedelta(hours=2)

                if data.get("error_message"):
                    job.error_message = data["error_message"]

                job.save()
                created_count += 1
                self.stdout.write(f"Created processing job: {job.name}")

        self.stdout.write(f"Created {created_count} processing jobs")
