from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum, F
from django.utils import timezone
from .models import ProcessingJob
from .serializers import (
    ProcessingJobSerializer,
    ProcessingJobCreateSerializer,
    ProcessingJobUpdateSerializer,
    ProcessingJobListSerializer,
    ProcessingJobDetailSerializer,
    ProcessingJobProgressSerializer,
    ProcessingJobResultSerializer,
    ProcessingJobActionSerializer,
    ProcessingJobFilterSerializer,
    ProcessingJobStatsSerializer,
    ProcessingJobBulkActionSerializer,
)

from .tasks import cancel_processing_job, retry_processing_job
from projects.permissions import IsProjectMember


class ProcessingJobListView(generics.ListAPIView):
    """List processing jobs."""

    permission_classes = [IsAuthenticated]
    serializer_class = ProcessingJobListSerializer
    queryset = ProcessingJob.objects.all().order_by("-created_at")

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by project if specified
        project_slug = self.request.query_params.get("project_slug")
        if project_slug:
            queryset = queryset.filter(project__slug=project_slug)

        # Filter by document if specified
        document_id = self.request.query_params.get("document_id")
        if document_id:
            queryset = queryset.filter(document_id=document_id)

        # Filter by job type
        job_type = self.request.query_params.get("job_type")
        if job_type:
            queryset = queryset.filter(job_type=job_type)

        # Filter by status
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by user
        user_id = self.request.query_params.get("user_id")
        if user_id:
            queryset = queryset.filter(created_by_id=user_id)

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        end_date = self.request.query_params.get("end_date")
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset


class ProcessingJobCreateView(generics.CreateAPIView):
    """Create a new processing job."""

    permission_classes = [IsAuthenticated]
    serializer_class = ProcessingJobCreateSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProcessingJobDetailView(generics.RetrieveAPIView):
    """Get processing job details."""

    permission_classes = [IsAuthenticated]
    serializer_class = ProcessingJobDetailSerializer
    queryset = ProcessingJob.objects.all()


class ProcessingJobUpdateView(generics.UpdateAPIView):
    """Update a processing job."""

    permission_classes = [IsAuthenticated]
    serializer_class = ProcessingJobUpdateSerializer
    queryset = ProcessingJob.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class ProcessingJobDeleteView(generics.DestroyAPIView):
    """Delete a processing job."""

    permission_classes = [IsAuthenticated]
    queryset = ProcessingJob.objects.all()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()


class ProcessingJobProgressView(generics.RetrieveAPIView):
    """Get processing job progress."""

    permission_classes = [IsAuthenticated]
    serializer_class = ProcessingJobProgressSerializer
    queryset = ProcessingJob.objects.all()


class ProcessingJobResultView(generics.RetrieveAPIView):
    """Get processing job results."""

    permission_classes = [IsAuthenticated]
    serializer_class = ProcessingJobResultSerializer
    queryset = ProcessingJob.objects.all()


class ProcessingJobActionView(generics.GenericAPIView):
    """Perform actions on processing jobs."""

    permission_classes = [IsAuthenticated]
    serializer_class = ProcessingJobActionSerializer

    def post(self, request, pk):
        job = get_object_or_404(ProcessingJob, pk=pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data["action"]

        if action == "cancel":
            if job.status in ["pending", "queued", "running"]:
                # Cancel the job
                cancel_processing_job.delay(job.id)
                job.status = "cancelled"
                job.save()
                message = "Job cancelled successfully"
            else:
                return Response(
                    {"error": "Cannot cancel job in current status"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        elif action == "retry":
            if job.status in ["failed", "cancelled"]:
                # Retry the job
                retry_processing_job.delay(job.id)
                job.status = "pending"
                job.retry_count += 1
                job.save()
                message = "Job queued for retry"
            else:
                return Response(
                    {"error": "Cannot retry job in current status"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        elif action == "pause":
            if job.status == "running":
                job.status = "paused"
                job.save()
                message = "Job paused successfully"
            else:
                return Response(
                    {"error": "Cannot pause job in current status"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        elif action == "resume":
            if job.status == "paused":
                job.status = "running"
                job.save()
                message = "Job resumed successfully"
            else:
                return Response(
                    {"error": "Cannot resume job in current status"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(
                {"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"message": message, "job_id": job.id, "status": job.status})


class ProcessingJobFilterView(generics.ListAPIView):
    """Filter processing jobs with advanced criteria."""

    permission_classes = [IsAuthenticated]
    serializer_class = ProcessingJobListSerializer

    def get_queryset(self):
        serializer = ProcessingJobFilterSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)

        filters = serializer.validated_data
        queryset = ProcessingJob.objects.all()

        # Apply filters
        if filters.get("project_slug"):
            queryset = queryset.filter(project__slug=filters["project_slug"])

        if filters.get("document_id"):
            queryset = queryset.filter(document_id=filters["document_id"])

        if filters.get("job_type"):
            queryset = queryset.filter(job_type=filters["job_type"])

        if filters.get("status"):
            queryset = queryset.filter(status__in=filters["status"])

        if filters.get("created_by"):
            queryset = queryset.filter(created_by_id=filters["created_by"])

        if filters.get("priority_min"):
            queryset = queryset.filter(priority__gte=filters["priority_min"])

        if filters.get("priority_max"):
            queryset = queryset.filter(priority__lte=filters["priority_max"])

        if filters.get("start_date"):
            queryset = queryset.filter(created_at__gte=filters["start_date"])

        if filters.get("end_date"):
            queryset = queryset.filter(created_at__lte=filters["end_date"])

        if filters.get("processing_time_min"):
            queryset = queryset.filter(
                processing_time__gte=filters["processing_time_min"]
            )

        if filters.get("processing_time_max"):
            queryset = queryset.filter(
                processing_time__lte=filters["processing_time_max"]
            )

        # Order by
        order_by = filters.get("order_by", "-created_at")
        queryset = queryset.order_by(order_by)

        return queryset


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def processing_job_stats(request):
    """Get processing job statistics."""
    # Overall statistics
    total_jobs = ProcessingJob.objects.count()
    completed_jobs = ProcessingJob.objects.filter(status="completed").count()
    failed_jobs = ProcessingJob.objects.filter(status="failed").count()
    running_jobs = ProcessingJob.objects.filter(status="running").count()
    pending_jobs = ProcessingJob.objects.filter(status="pending").count()

    # Job type distribution
    job_type_stats = (
        ProcessingJob.objects.values("job_type")
        .annotate(
            count=Count("id"),
            completed=Count("id", filter=Q(status="completed")),
            failed=Count("id", filter=Q(status="failed")),
            running=Count("id", filter=Q(status="running")),
        )
        .order_by("-count")
    )

    # Status distribution
    status_stats = (
        ProcessingJob.objects.values("status")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Performance statistics
    performance_stats = ProcessingJob.objects.filter(status="completed").aggregate(
        avg_processing_time=Avg("processing_time"),
        avg_memory_usage=Avg("memory_usage"),
        avg_cpu_usage=Avg("cpu_usage"),
    )

    # User statistics
    user_stats = (
        ProcessingJob.objects.values("created_by__username")
        .annotate(
            total_jobs=Count("id"),
            completed_jobs=Count("id", filter=Q(status="completed")),
            failed_jobs=Count("id", filter=Q(status="failed")),
        )
        .order_by("-total_jobs")
    )

    # Recent activity
    recent_jobs = ProcessingJob.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()

    stats = {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "running_jobs": running_jobs,
        "pending_jobs": pending_jobs,
        "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
        "job_type_distribution": list(job_type_stats),
        "status_distribution": list(status_stats),
        "performance_stats": performance_stats,
        "user_stats": list(user_stats),
        "recent_jobs": recent_jobs,
    }

    serializer = ProcessingJobStatsSerializer(stats)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def project_processing_stats(request, project_slug):
    """Get processing statistics for a specific project."""
    from projects.models import Project

    project = get_object_or_404(Project, slug=project_slug)

    # Project-specific job statistics
    project_jobs = ProcessingJob.objects.filter(project=project)

    total_jobs = project_jobs.count()
    completed_jobs = project_jobs.filter(status="completed").count()
    failed_jobs = project_jobs.filter(status="failed").count()
    running_jobs = project_jobs.filter(status="running").count()

    # Job type distribution for project
    job_type_stats = (
        project_jobs.values("job_type")
        .annotate(
            count=Count("id"),
            completed=Count("id", filter=Q(status="completed")),
            failed=Count("id", filter=Q(status="failed")),
        )
        .order_by("-count")
    )

    # Processing time statistics
    processing_time_stats = project_jobs.filter(status="completed").aggregate(
        avg_time=Avg("processing_time"),
        min_time=Avg("processing_time"),
        max_time=Avg("processing_time"),
    )

    # Recent activity
    recent_jobs = project_jobs.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()

    stats = {
        "project_name": project.name,
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "running_jobs": running_jobs,
        "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
        "job_type_distribution": list(job_type_stats),
        "processing_time_stats": processing_time_stats,
        "recent_jobs": recent_jobs,
    }

    return Response(stats)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def processing_job_bulk_action(request):
    """Perform bulk actions on processing jobs."""
    serializer = ProcessingJobBulkActionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    action = serializer.validated_data["action"]
    job_ids = serializer.validated_data["job_ids"]

    jobs = ProcessingJob.objects.filter(id__in=job_ids)

    if action == "cancel":
        # Cancel all jobs that can be cancelled
        cancellable_jobs = jobs.filter(status__in=["pending", "queued", "running"])
        for job in cancellable_jobs:
            cancel_processing_job.delay(job.id)
            job.status = "cancelled"
            job.save()

        message = f"{cancellable_jobs.count()} jobs cancelled"
        affected_count = cancellable_jobs.count()

    elif action == "retry":
        # Retry all failed or cancelled jobs
        retryable_jobs = jobs.filter(status__in=["failed", "cancelled"])
        for job in retryable_jobs:
            retry_processing_job.delay(job.id)
            job.status = "pending"
            job.retry_count += 1
            job.save()

        message = f"{retryable_jobs.count()} jobs queued for retry"
        affected_count = retryable_jobs.count()

    elif action == "delete":
        # Soft delete all jobs
        for job in jobs:
            job.is_deleted = True
            job.deleted_at = timezone.now()
            job.deleted_by = request.user
            job.save()

        message = f"{jobs.count()} jobs deleted"
        affected_count = jobs.count()

    else:
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": message, "affected_count": affected_count})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def processing_queue_status(request):
    """Get current processing queue status."""
    # Count jobs by status
    queue_stats = ProcessingJob.objects.aggregate(
        pending=Count("id", filter=Q(status="pending")),
        queued=Count("id", filter=Q(status="queued")),
        running=Count("id", filter=Q(status="running")),
        completed=Count("id", filter=Q(status="completed")),
        failed=Count("id", filter=Q(status="failed")),
        cancelled=Count("id", filter=Q(status="cancelled")),
    )

    # Get oldest pending job
    oldest_pending = (
        ProcessingJob.objects.filter(status="pending").order_by("created_at").first()
    )

    # Get longest running job
    longest_running = (
        ProcessingJob.objects.filter(status="running").order_by("started_at").first()
    )

    # Calculate average wait time
    avg_wait_time = ProcessingJob.objects.filter(
        status__in=["completed", "failed"], started_at__isnull=False
    ).aggregate(avg_wait=Avg(F("started_at") - F("created_at")))["avg_wait"]

    queue_status = {
        "queue_stats": queue_stats,
        "oldest_pending_job": {
            "id": oldest_pending.id,
            "created_at": oldest_pending.created_at,
            "wait_time": timezone.now() - oldest_pending.created_at
            if oldest_pending
            else None,
        }
        if oldest_pending
        else None,
        "longest_running_job": {
            "id": longest_running.id,
            "started_at": longest_running.started_at,
            "running_time": timezone.now() - longest_running.started_at
            if longest_running
            else None,
        }
        if longest_running
        else None,
        "average_wait_time": avg_wait_time,
    }

    return Response(queue_status)
