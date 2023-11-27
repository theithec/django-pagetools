"""
Add static.serve for MEDIA:ROOT if debug == True
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [

            path('tinymce/', include('tinymce.urls')),

        ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
