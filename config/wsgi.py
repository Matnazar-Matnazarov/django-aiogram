"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Django application setup should be before any other imports
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

