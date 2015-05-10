# Django settings for demo project.

import os
from os.path import dirname
BASE_DIR = dirname(dirname(__file__))
DEBUG = True
TEMPLATE_DEBUG = DEBUG


def _(s):
    return s

ADMINS = (('admin', 'root@localhost'),)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db'),
    }
}

ALLOWED_HOSTS = ['127.0.0.1:8000', ]

TIME_ZONE = 'America/Chicago'

LANGUAGES = (('en', _('English')),
             ('de', _('German')),)


SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.sep.join((BASE_DIR, 'media',))
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.sep.join((BASE_DIR, 'static',))

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'djangobower.finders.BowerFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'r-cf&895wb44n%%z-+=4-ds^2bysdubz(*s+yqbvy-ef5*h*4o'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}
CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = ""
ROOT_URLCONF = 'project.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'project.wsgi.application'

TEMPLATE_DIRS = (
    os.sep.join((BASE_DIR, 'templates',)),
    )
BOWER_COMPONENTS_ROOT = os.sep.join((BASE_DIR, '',))
BOWER_INSTALLED_APPS = (
    'bootstrap',
    'jquery-ui'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'debug_toolbar',
    'crispy_forms',
    'grappelli.dashboard',
    'mptt',
    'grappelli',
    'filebrowser',
    'djangobower',
    'reversion',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'pagetools.core',
    'pagetools.pages',
    'pagetools.widgets',
    'pagetools.menus',
    'pagetools.search',
    'pagetools.subscribe',
    'pagetools.gallery',
    'main',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    # 'django.core.context_processors.media',
    'django.core.context_processors.static',
    )

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

INTERNAL_IPS = ('127.0.0.1',)

GRAPPELLI_ADMIN_TITLE = '<a href="/" target="_blank">pagetools_demo</a>'

CRISPY_TEMPLATE_PACK = 'bootstrap'
PT_MENU_TEMPLATE = 'bootstrap_nav_menu.html'

PT_PAGE_PREFIX = 'page/'

PT_TEMPLATETAG_WIDGETS = {
    _('Time'): ('main.templatetags.main_tags', 'CurrentTimeNode'),
    _('NewsMonthList'): ('main.templatetags.main_tags', 'NewsMonthNode'),
}
GRAPPELLI_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'

'''
if DEBUG:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    INSTALLED_APPS += (
        'debug_toolbar',
        'django_nose',
    )
    DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}
'''
