# pylint: disable=unused-argument
# for request object
import datetime
from smtplib import SMTPException
from typing import Any

from django import template
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.http.request import HttpRequest
from django.http.response import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from pagetools.utils import import_cls

from . import settings as subs_settings
from .models import Subscriber


def _send_mail(subscriber, template_name, context, subject, attachmentfile=None):
    domain = Site.objects.get_current().domain
    context.update({"site_name": Site.objects.get_current().name, "site_domain": domain, "subscriber": subscriber})
    tmpl = template.loader.get_template(template_name + ".txt")
    msg = tmpl.render(context)
    try:
        tmpl = template.loader.get_template(template_name + ".html")
        htmlmsg = tmpl.render(context)
    except template.exceptions.TemplateDoesNotExist:
        htmlmsg = None
    email = EmailMultiAlternatives(subject, msg, subs_settings.NEWS_FROM, [subscriber.email])
    if htmlmsg:
        email.attach_alternative(htmlmsg, "text/html")
    if attachmentfile:
        email.attach_file(attachmentfile)
    try:
        email.send()
    except SMTPException:
        return False

    return True  # send_mail


def _send_activation_mail(subscriber, template_name):
    subject = subs_settings.ACTIVATION_MAIL_SUBJECT
    return _send_mail(subscriber, template_name, {}, subject)


def _subscribe(request, mail_success_template_name="subscriptions/activation_msg"):
    subscribe_form = import_cls(subs_settings.SUBSCRIPTION_FORM)
    form = subscribe_form(request.POST)
    if form.is_valid():
        clean_data = form.clean()
        email = clean_data["email"]
        already_there = Subscriber.objects.filter(email=email).exists()
        if not already_there:
            subscriber = Subscriber(email=email, is_activated=False, lang=get_language())
            mail_success = _send_activation_mail(subscriber, mail_success_template_name)
            if mail_success:
                subscriber.save()
            else:
                form.add_error(_("An error occurred"))
    return form


def _subscribe_fallback(request, form, msg):
    context = {"msg": msg}
    if form.errors:
        context["form"] = form
    return render(request, "subscriptions/subscribe_result.html", context)


def _subscribe_json(form, msg):
    return JsonResponse({"form": form.as_p(), "errors": form.errors, "msg": msg})


def subscribe(request):
    if request.method == "GET":
        raise Http404
    form = _subscribe(request)
    # if form.errors:
    if form.is_valid():
        msg = subs_settings.SUBSCRIPTION_SUCCESS_MSG % form.cleaned_data["email"]
    else:
        msg = _("An error occurred")
    if request.is_ajax():
        return _subscribe_json(form, msg)
    level = messages.ERROR if form.errors else messages.SUCCESS
    messages.add_message(request, level, msg)
    return _subscribe_fallback(request, form, msg)


def _matching_activated_subscriber(request: HttpRequest, key: Any) -> Subscriber:
    subscriber = get_object_or_404(Subscriber, key=key)
    return subscriber


def _activate(request, key):
    subscriber = _matching_activated_subscriber(request, key)
    if subscriber:
        activate_end = subscriber.subscribtion_date + datetime.timedelta(hours=48)
        if not subscriber.is_activated and activate_end > timezone.now():
            subscriber.activate()
            messages.add_message(request, messages.SUCCESS, subs_settings.ACTIVATION_SUCCESS_MSG)
            return subscriber
    return None


def activate(request, key):
    if _activate(request, key):
        return render(request, subs_settings.MSG_BASE_TEMPLATE)  # , {"msg": _("activation: ok")}
    raise Http404()


def unsubscribe(request, key):
    subscriber = _matching_activated_subscriber(request, key)
    if subscriber and subscriber.is_activated:
        subscriber.delete()
        messages.add_message(request, messages.SUCCESS, _("unsubscribe: ok"))
        return render(request, subs_settings.MSG_BASE_TEMPLATE, {"msg": _("unsubscribe: ok")})
    raise Http404()
