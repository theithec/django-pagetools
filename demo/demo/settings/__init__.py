"""
Django settings for demo project.
Generated by 'django-admin startproject' using Django 1.9.9.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECRET_KEY = "#c##*+s7^=1m^p-=m&fvs8v(8p&#esxlqbq_3i+v(5)4z3ud)@"
DEBUG = True
ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = [
    "tinymce",
    "grappelli.dashboard",  # optional (pagetools provides two dashboard modules),
    # needs further configuration
    "grappelli",  # required
    "filebrowser",  # required
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # required for search
    "crispy_forms",  # required for pages
    "crispy_forms_foundation",
    "sekizai",  # required for sections. Needs further configuration
    "polls",
    "main.apps.MainConfig",
    "demo_sections",
    "pagetools",  # needed for all pagetools modules
    "pagetools.widgets",  # Widgets (e.g. for sidebars)
    "pagetools.pages",  # Simple Pages
    "pagetools.menus",  #
    "pagetools.sections",  # Nested Content (e.g. for a singlepage site)
    "pagetools.search",  # Simple Search on database fields
    "pagetools.subscriptions",  # Subscriptions to whatever
    "captcha",
    "debug_toolbar",
]

SITE_ID = 1  # required by contrib.sites

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "demo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "sekizai.context_processors.sekizai",
                "pagetools.widgets.context_processors.pagetype_from_view",
            ],
        },
    },
]

WSGI_APPLICATION = "demo.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]



TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "/tmp/debug.log",
        },
    },
    "loggers": {
        "pagetools": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "static_root")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
GRAPPELLI_INDEX_DASHBOARD = "dashboard.CustomIndexDashboard"
ADMIN_URL = r"^admin/"
PT_TEMPLATETAG_WIDGETS = {
    "subscribe": "pagetools.subscriptions.templatetags.subscriptions_tags.SubscribeNode",
    "latest_question": "main.templatetags.LatestQuestionNode",
}
PT_MENU_TEMPLATE = "foundation6_nav_menu.html"
PT_MAILFORM_RECEIVERS = ["nobody@localhost.localdomain"]
INTERNAL_IPS = ["127.0.0.1"]
from crispy_forms_foundation.settings import *

TINYMCE_DEFAULT_CONFIG = {
    "theme": "silver",
    "height": 500,
    "menubar": False,
    "plugins": "link,advlist,autolink,lists,link,image,charmap,print,preview,anchor,"
    "searchreplace,visualblocks,code,fullscreen,insertdatetime,media,table,paste,"
    "code,help,wordcount",
    "toolbar": "undo redo | formatselect | "
    "bold italic backcolor | alignleft aligncenter "
    "alignright alignjustify | bullist numlist outdent indent | "
    "removeformat | link |help",
}
X_FRAME_OPTIONS = "SAMEORIGIN"
PAGINATE_BY = 5
PAGINATION_NUM_PAGELINKS = 5
LANGUAGE_CODE = "en-us"
LANGUAGE_CODE="de-de"