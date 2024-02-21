from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import django

import dotenv

dotenv_path = '/home/e-lec-tron/Documents/github repos/DynaTests-backend/backend/.env'
print(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'), "here")
dotenv.read_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')
app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()