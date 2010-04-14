from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

DEPENDENCIES = [
    'projecter.apps.accounts'
]

def check_dependencies():
    for app in DEPENDENCIES:
        if app not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured("The %s application must be in INSTALLED_APPS" % app)

check_dependencies()
        
