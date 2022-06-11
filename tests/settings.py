import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR + "/demo")
SECRET_KEY = "#c##*+s7^=1m^p-=m&fvs8v(8p&#esxlqbq_3i+v(5)4z3ud)@"
DEBUG = False
ALLOWED_HOSTS = ["*"]
SITE_ID = 1  # required by contrib.sites
MIDDLEWARE_CLASSES = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
INSTALLED_APPS = [
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
    "sekizai",  # required for sections. Needs further configuration
    "django_ajax",
    "pagetools",  # needed for all pagetools modules
    "pagetools.widgets",  # Widgets (e.g. for sidebars)
    "pagetools.pages",  # Simple Pages
    "pagetools.menus",  #
    "pagetools.sections",  # Nested Content (e.g. for a singlepage site)
    "pagetools.search",  # Simple Search on database fields
    "pagetools.subscriptions",  # Subscriptions to whatever
    "captcha",
    # 'debug_toolbar',
    "polls",
    "demo_sections",
    # "main",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "tests", "templates/"), os.path.join(BASE_DIR, "demo", "templates/")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "sekizai.context_processors.sekizai",
                "pagetools.widgets.context_processors.pagetype_from_view",
            ],
        },
    },
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
ROOT_URLCONF = "tests.urls"
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "static_root")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "demo", "media")
GRAPPELLI_INDEX_DASHBOARD = "tests.dashboard.CustomIndexDashboard"


ADMIN_URL = r"^admin/"

PT_TEMPLATETAG_WIDGETS = {
    "subscribe": "pagetools.subscriptions.templatetags.subscriptions_tags.SubscribeNode",
    "latest_question": "main.templatetags.LatestQuestionNode",
}
PT_MENU_TEMPLATE = "foundation6_nav_menu.html"
