import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'overlytics.settings')
app = Celery('overlytics')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'sync-all-projects-hourly': {
        'task': 'apps.dashboard.tasks.sync_all_projects',
        'schedule': crontab(minute=0),   # every hour at :00
    },
}
