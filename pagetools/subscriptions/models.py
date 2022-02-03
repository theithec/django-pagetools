import datetime
import smtplib
import string
import random
from hashlib import sha224 as sha

from urllib.parse import quote
from django.apps import apps
from django.core.mail import get_connection
from django.core.mail.message import EmailMessage
from django.db import models
from django.db.utils import ProgrammingError
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pagetools.models import LangManager, LangModel

from . import settings as subs_settings
from .base_models import BaseSubscriberMixin


def _mk_key():
    key = "".join([random.choice(string.ascii_letters + string.digits) for x in range(1, 32)])
    try:
        if Subscriber.objects.filter(key=key):
            key = _mk_key()
    except ProgrammingError:  # due migrations
        pass
    return key


class Subscriber(BaseSubscriberMixin, LangModel):
    key = models.CharField(max_length=32, default=_mk_key)
    email = models.EmailField(unique=True)
    objects = LangManager()

    def activate(self):
        self.is_activated = True
        self.subscribtion_date = datetime.date(1900, 1, 1)
        self.save()

    def get_email(self):
        return self.email

    @classmethod
    def get_subscribers(cls, **kwargs):
        fkwargs = {"is_activated": True}
        if subs_settings.SUBSCRIBER_LANG_ONLY:
            fkwargs["lang"] = kwargs.pop("lang", None)

        return cls.objects.lfilter(**fkwargs)


# http://djangosnippets.org/snippets/1993/
# django-mailer, django-mail-queue, ... alle doof
#        choices=(
#            (-1, 'SMTP Fail'),
#            (0, 'Queued'),
#            (1, 'Sent OK'),
#            (2, 'Unexpected Error'),
#        ))
class QueuedEmail(LangModel):
    class Meta:
        abstract = False
        verbose_name = _("News-Mail")

    createdate = models.DateTimeField("Created on", auto_now_add=True, blank=True, editable=False)

    modifydate = models.DateTimeField("Last modified on", auto_now_add=True, blank=True, editable=False)

    senddate = models.DateTimeField("Send after", auto_now_add=True, blank=True, editable=True)

    subject = models.CharField(verbose_name="Subject", default="", unique=False, blank=True, max_length=255)

    body = models.TextField(verbose_name="Body", default="", unique=False, blank=True)

    def save(self, *args, **kwargs):
        self.modifydate = timezone.now()

        super(QueuedEmail, self).save()  # force_insert, force_update)
        modelname = subs_settings.SUBSCRIBER_MODEL
        if modelname == "Subscriber":
            modelname = "subscriptions.Subscriber"
        subscr_model = apps.get_model(*modelname.rsplit(".", 1))
        kwargs["lang"] = self.lang
        subscribers = subscr_model.get_subscribers(**kwargs)

        for subscr in subscribers:
            SendStatus(subscriber=subscr, queued_email=self, status=0).save()

    def send_to(self, to, conn, unsubscribe_path):
        status = -1
        if self.senddate < timezone.now():
            if self.subject and self.body:
                if to:
                    try:
                        msg = EmailMessage(
                            "%s" % self.subject,
                            self.body.replace("__unsubscribe_path__", unsubscribe_path),
                            subs_settings.NEWS_FROM,
                            [to],
                            connection=conn,
                        )
                        msg.content_subtype = "html"  # Main content is now text/html
                        status = msg.send(
                            fail_silently=True,
                        )
                    except smtplib.SMTPException:
                        pass
        return status

    def send_to_all(self, sendstatuses):
        if self.senddate < timezone.now():
            conn = get_connection()
            for sendstatus in sendstatuses:
                status = self.send_to(
                    sendstatus.subscriber.get_email(),
                    conn,
                    reverse(
                        "subscriptions:unsubscribe",
                        kwargs={"key": sendstatus.subscriber.key},
                    ),
                )
                if status == 1:
                    if sendstatus.subscriber.failures != 0:
                        sendstatus.subscriber.failures = 0
                        sendstatus.subscriber.save()
                    sendstatus.delete()
                else:
                    sendstatus.status = status
                    subscriber = sendstatus.subscriber
                    subscriber.failures += 1
                    subscriber.save()
                    if subscriber.failures > subs_settings.MAX_FAILURES:
                        SendStatus.objects.filter(subscriber=subscriber).delete()
                        subscriber.delete()
                    else:
                        sendstatus.save()

    def __str__(self):
        return self.subject


class SendStatus(models.Model):
    subscriber = models.ForeignKey(subs_settings.SUBSCRIBER_MODEL, on_delete=models.CASCADE)
    queued_email = models.ForeignKey(QueuedEmail, on_delete=models.CASCADE)
    status = models.IntegerField()

    def __str__(self):
        return "%s  / %s : %s" % (self.subscriber, self.queued_email, self.status)

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statuses"
