from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.template.response import TemplateResponse
from django.urls import path

from .models import QueuedEmail, SendStatus, Subscriber


class SubscriberAdmin(admin.ModelAdmin):
    change_list_template = "admin/subscriptions/subscriber/sub_change_list.html"
    list_display = ("email", "subscribtion_date", "is_activated")
    date_hierarchy = "subscribtion_date"
    readonly_fields = ["subscribtion_date"]
    list_editable = ["is_activated"]
    list_filter = ["is_activated"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "mass_subscription/",
                self.mass_subscription,
                name="pagetools_subscriptions_mass_subscription",
            ),
        ]
        return my_urls + urls

    def mass_subscription(self, request):
        context = {}
        if request.method == "POST":
            failed = []
            for entry in request.POST["entries"].splitlines():
                entry = entry.strip()
                if not entry:
                    continue
                try:
                    validate_email(entry)
                    Subscriber.objects.get_or_create(email=entry, is_activated=True)
                except ValidationError:
                    failed.append(entry)
            context["failures"] = failed

        return TemplateResponse(
            request,
            "admin/subscriptions/subscriber/mass_subscription.html",
            context=context,
        )


admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(QueuedEmail)
admin.site.register(SendStatus)
