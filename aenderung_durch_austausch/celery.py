import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aenderung_durch_austausch.settings')
app = Celery('aenderung-durch-austausch')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
