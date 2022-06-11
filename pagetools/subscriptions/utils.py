from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.translation import activate, get_language

from . import settings as subs_settings
from .models import QueuedEmail, SendStatus


def to_queue(content, **kwargs):
    lang = content.get("lang", None) or kwargs.get("lang", None)
    orglang = get_language()
    if lang:
        activate(lang)
    else:
        activate(orglang)
    site = Site.objects.get_current()
    msg = render_to_string(
        "subscriptions/msg.html",
        {
            "title": content["title"],
            "content": content["body"],
            "site_name": site.name,
            "site_domain": site.domain,
        },
    )
    mail = QueuedEmail(
        subject="%s %s" % (subs_settings.NEWS_SUBJECT_PREFIX, content["title"]),
        body=msg,
        lang=lang,
    )
    mail.save()
    activate(orglang)


def send_queued_mail(mail: QueuedEmail, maxmails):
    sts = SendStatus.objects.filter(queued_email=mail)[:maxmails]
    mail.send_to_all(sts)
    sst2 = SendStatus.objects.filter(queued_email=mail)
    if not sst2 and subs_settings.DELETE_QUEUED_MAILS:
        mail.delete()
    return len(sts)


def send_max(max_send=subs_settings.MAX_PER_TIME):
    mails = QueuedEmail.objects.all()
    num_sended = 0
    for mail in mails:
        maxmails = max_send - num_sended
        if maxmails < 1:
            break
        num_sended += send_queued_mail(mail, maxmails)


# influenced by:
# http://stackoverflow.com/questions/7583801/send-mass-emails-with-emailmultialternatives
