"""
WSGI config for bicitaxi_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""
import os
import sys
import site
from django.core.wsgi import get_wsgi_application

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/root/bicitaxi-env/lib/python3.6/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/root/bicitaxi-env/lib/python3.6')

sys.path.append('/var/www/bicitaxi-api')
sys.path.append('/var/www/bicitaxi-api/bicitaxi_api')

os.environ['DJANGO_SETTINGS_MODULE'] = 'bicitaxi_api.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bicitaxi_api.settings')

application = get_wsgi_application()
