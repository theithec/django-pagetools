from  . import *
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(3,  "debug_toolbar.middleware.DebugToolbarMiddleware")