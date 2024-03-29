"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import dotenv

from django.core.wsgi import get_wsgi_application
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables from the .env file
env_file = os.path.join(PROJECT_DIR, '.env')
dotenv.read_dotenv(env_file)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()
app = application