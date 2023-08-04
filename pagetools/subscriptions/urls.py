from django.urls import path

from .views import activate, subscribe, unsubscribe


app_name = "subscriptions"

urlpatterns = [
    path("subscribe/", subscribe, name="subscribe"),
    path("activate/<str:key>/", activate, name="activate"),
    path("unsubscribe/<str:key>/", unsubscribe, name="unsubscribe"),
]
