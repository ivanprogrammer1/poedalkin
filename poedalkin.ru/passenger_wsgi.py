# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, '/var/www/u1765928/data/www/poedalkin.ru/project')
sys.path.insert(1, '/var/www/u1765928/data/venv/lib/python3.10/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()