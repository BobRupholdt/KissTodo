# Django settings for kisstodo project.

KISSTODO_USE_GAE=True

if KISSTODO_USE_GAE: from djangoappengine.settings_base import *

import os

SECRET_KEY = '7vyl7&d^725^kllplihdr2f#a7q15c#gcdlaih4h^-%93v%36^'

DEBUG = False
#DEBUG = True
TEMPLATE_DEBUG = DEBUG

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'static')
MEDIA_URL = '/static/'
ROOT_URLCONF = 'urls'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

if KISSTODO_USE_GAE:
    INSTALLED_APPS = (
        'todo', # barmassimo
        'django.contrib.admin',
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',
        'djangotoolbox',
        'django.contrib.humanize',
        'djangoappengine', # djangoappengine should come last, so it can override a few manage.py commands
    )
else:
    INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
	'todo',
	'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.humanize',
)

MIDDLEWARE_CLASSES = (
    #'todo.middleware.AjaxMiddleware.AjaxMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', # barmassimo
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# Activate django-dbindexer if available
if KISSTODO_USE_GAE:
    try:
        import dbindexer
        DATABASES['native'] = DATABASES['default']
        DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native'}
        INSTALLED_APPS += ('dbindexer',)
        DBINDEXER_SITECONF = 'dbindexer'
        MIDDLEWARE_CLASSES = ('dbindexer.middleware.DBIndexerMiddleware',) + \
                             MIDDLEWARE_CLASSES
    except ImportError:
        pass
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'kisstodo.db',           # Or path to database file if using sqlite3.
            'USER': '',                      # Not used with sqlite3.
            'PASSWORD': '',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
USE_I18N = True
USE_L10N = True

# List of callables that know how to import templates from various sources.    
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
)

# This test runner captures stdout and associates tracebacks with their
# corresponding output. Helps a lot with print-debugging.
TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'

ADMIN_MEDIA_PREFIX = '/media/admin/'
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)    
