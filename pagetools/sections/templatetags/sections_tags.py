from django import template
from django.template.loader import (render_to_string, get_template,
                                    select_template)
from django.template import Context, Template

from pagetools.sections.utils import get_template_names_for_obj
from pagetools.sections import render_node_extradata

register = template.Library()


class ContentNode(template.Node):
    template_names_suffix = ""

    def __init__(self, obj, user, suffix):
        self.object_var = template.Variable(obj)
        self.user_var = template.Variable(user)
        self.suffix_var = None
        if suffix:
            self.suffix_var = template.Variable(suffix)

    def render(self, context):
        obj = self.object_var.resolve(context)
        user = self.user_var.resolve(context)
        suffix = ""
        if self.suffix_var:
            suffix = self.suffix_var.resolve(context)
        real_template = get_template_names_for_obj(obj, suffix)
        for k, v in render_node_extradata.items():
            context[k] = v
        context['object'] = obj
        if obj.positioned_content:
            context['contents'] = obj.ordered_content(user=user)
        if not obj.enabled:
            context['unpublished'] = True

        return select_template(real_template).render(context)


@register.tag
def render_node(parser, token, *args, **kwargs):
    splitted = token.contents.split()
    obj, user = splitted[1:3]
    suffix = splitted[-1] if len(splitted) > 3 else ""
    return ContentNode(obj, user, suffix)


@register.filter(name='ordered_content')
def _ordered_content(value, args):
    obj = value
    if obj is None:
        return []
    return obj.ordered_content(user=args)
