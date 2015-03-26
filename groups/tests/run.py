#! /usr/bin/env python3
"""From http://stackoverflow.com/a/12260597/400691"""
import sys
from optparse import make_option, OptionParser

import dj_database_url
import django
from colour_runner.django_runner import ColourRunnerMixin
from django.conf import settings
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS


settings.configure(
    CRISPY_TEMPLATE_PACK='bootstrap3',
    DATABASES={
        'default': dj_database_url.config(default='postgres://localhost/groups'),
    },
    INSTALLED_APPS=(
        'groups',
        'groups.tests',

        'crispy_forms',
        # Put contenttypes before auth to work around test issue.
        # See: https://code.djangoproject.com/ticket/10827#comment:12
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.admin',
    ),
    PASSWORD_HASHERS=('django.contrib.auth.hashers.MD5PasswordHasher',),
    ROOT_URLCONF='groups.tests.urls',
    MIDDLEWARE_CLASSES=(
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    ),
    TEMPLATE_CONTEXT_PROCESSORS=TEMPLATE_CONTEXT_PROCESSORS + (
        'django.core.context_processors.request',
    ),
)

try:
    django.setup()
except AttributeError:
    pass


from django.test.runner import DiscoverRunner  # noqa hack for DJANGO_LT_17


class Runner(ColourRunnerMixin, DiscoverRunner):
    pass


option_list = (
    make_option(
        '-v', '--verbosity', action='store', dest='verbosity', default='1',
        type='choice', choices=['0', '1', '2', '3'],
        help=('Verbosity level; 0=minimal output, 1=normal output, ' +
              '2=verbose output, 3=very verbose output'),
    ),
)

parser = OptionParser(option_list=option_list)
options, args = parser.parse_args()

test_runner = Runner(verbosity=int(options.verbosity))
failures = test_runner.run_tests(args)
if failures:
    sys.exit(1)
