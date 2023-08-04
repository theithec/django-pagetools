from unittest import mock

from django.conf import settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core import mail
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from pagetools.subscriptions.models import Subscriber
from pagetools.subscriptions.views import activate


class ViewTest(TestCase):
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def _test_add_subscriber(self):
        settings.DEBUG = True
        url = reverse("subscriptions:subscribe", args=[])
        self.client.post(url, {"email": "q@w.de"})
        subs = Subscriber.objects.all()
        self.assertTrue(len(subs), 1)
        self.assertTrue(len(mail.outbox), 1)

    def test_activate(self):
        self._test_add_subscriber()
        sub = Subscriber.objects.get(email="q@w.de")
        self.assertFalse(sub.is_activated)
        factory = RequestFactory()
        url = reverse("subscriptions:activate", kwargs={"key": sub.key})
        request = factory.get(url)
        setattr(request, "session", "session")
        setattr(request, "resolver_match", mock.Mock(func=activate))
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        self.assertFalse(sub.is_activated)
        activate(request, sub.key)
        sub.refresh_from_db()
        self.assertTrue(sub.is_activated)
