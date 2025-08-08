import os 
from celery import Celery
from django.conf import settings
from core import task


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_system.settings')
app = Celery('credit_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

