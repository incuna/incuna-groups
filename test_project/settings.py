import os

import dj_database_url
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True
ALLOWED_HOSTS = []
ROOT_URLCONF = 'groups.tests.urls'
STATIC_URL = '/static/'

SECRET_KEY = 'krc34ji^-fd-=+r6e%p!0u0k9h$9!q*_#l=6)74h#o(jrxsx4p'
PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)

DATABASES = {
    'default': dj_database_url.config(default='postgres://localhost/groups')
}
DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'

INSTALLED_APPS = (
    'groups',
    'groups.tests',

    'crispy_forms',
    'polymorphic',

    # Put contenttypes before auth to work around test issue.
    # See: https://code.djangoproject.com/ticket/10827#comment:12
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)
TEMPLATE_CONTEXT_PROCESSORS = TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

CRISPY_TEMPLATE_PACK = 'bootstrap3'

TEST_RUNNER = 'test_project.test_runner.Runner'
