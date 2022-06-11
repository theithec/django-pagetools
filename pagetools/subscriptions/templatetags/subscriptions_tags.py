from django import template

from pagetools.subscriptions.forms import SubscribeForm


register = template.Library()


class SubscribeNode(template.Node):
    def render(self, context):
        request = context.pop("request")
        tmpl = template.loader.get_template("subscriptions/block_subscription.html")
        context["sform"] = SubscribeForm()
        return tmpl.render(context, request=request)


@register.tag(name="subscribe_widget")
def do_subscribe_node(_parser, _token):
    return SubscribeNode()
