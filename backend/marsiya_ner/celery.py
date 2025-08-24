import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marsiya_ner.settings')

app = Celery('marsiya_ner')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# Celery Beat Schedule
app.conf.beat_schedule = {
    'cleanup-old-jobs': {
        'task': 'processing.tasks.cleanup_old_jobs',
        'schedule': 86400.0,  # 24 hours
    },
    'update-entity-counts': {
        'task': 'documents.tasks.update_entity_counts',
        'schedule': 21600.0,  # 6 hours
    },
}

# Celery Configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
)
