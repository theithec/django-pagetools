from django.conf import settings


def _(_x):
    return _x


MSG_BASE_TEMPLATE = getattr(settings, "PT_SUBSCR_MSG_BASE_TEMPLATE", "base.html")

NEWS_FROM = getattr(settings, "PT_SUBSCR_NEWS_FROM", "news@localhost")

NEWS_SUBJECT_PREFIX = getattr(settings, "PT_SUBSCR_SUBJECT_PREFIX", "[News:]")

SUBSCRIPTION_SUCCESS_MSG = getattr(settings, "PT_SUBSCR_SUBSCRIPTION_SUCCESS_MSG", _("subscribed: %s"))

ACTIVATION_MAIL_SUBJECT = getattr(settings, "PT_SUBSCR_ACTIVATION_MAIL_SUBJECT", _("Welcome"))

ACTIVATION_SUCCESS_MAIL_SUBJECT = getattr(
    settings, "PT_SUBSCR_ACTIVATION_SUCCESS_MAIL_SUBJECT", _("Activation successfull")
)

ACTIVATION_SUCCESS_MSG = getattr(settings, "PT_SUBSCR_ACTIVATION_SUCCESS_MSG", _("activation: ok"))

MAX_PER_TIME = getattr(settings, "PT_SUBSCR_MAX_PER_TIME", 100)

# max. mail send failures in a row before subscriber is deleted
MAX_FAILURES = getattr(settings, "PT_SUBSCR_MAX_FAILURES", 8)

URLS_REGEX = getattr(settings, "PT_SUBSCR_URLS_REGEX", r"^subscribtion/")

SUBSCRIBER_MODEL = getattr(settings, "PT_SUBSCR_SUBSCRIBER_MODEL", "subscriptions.Subscriber")

SUBSCRIPTION_FORM = getattr(settings, "PT_SUBSCRIPTION_FORM", "pagetools.subscriptions.forms.SubscribeForm")


DELETE_QUEUED_MAILS = getattr(settings, "PT_DELETE_QUEUED_MAILS", True)

SUBSCRIBER_LANG_ONLY = getattr(settings, "PT_SUBSCRIBER_LANG_ONLY", False)
