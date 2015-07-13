"""
WSGI config for TestSite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TestSite.settings")
sys.path.append('/home/bischofs/1065/1065-Calculation-Tool/')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
