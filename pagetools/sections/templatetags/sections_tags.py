from django import template
from django.template.loader import select_template
from django.utils.safestring import mark_safe

from pagetools.sections.apps import SectionsConfig
from pagetools.sections.utils import get_template_names_for_obj


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
        suffix = ""
        if self.suffix_var:
            suffix = self.suffix_var.resolve(context)
        real_template = get_template_names_for_obj(obj, suffix)
        for key, val in SectionsConfig.render_node_extradata.items():
            context[key] = val
        context["object"] = obj
        if not obj.is_published:
            context["unpublished"] = True

        data = {}
        for dict_ in context.dicts:
            data.update(dict_)
        return select_template(real_template).render(data)


@register.tag
def render_node(_parser, token, *args, **kwargs):
    splitted = token.contents.split()
    obj, user = splitted[1:3]
    suffix = splitted[-1] if len(splitted) > 3 else ""
    return ContentNode(obj, user, suffix)


@register.filter(name="ordered_content")
def _ordered_content(value, args):
    obj = value
    if obj is None:
        return []
    return obj.ordered_content(user=args)


@register.simple_tag(name="rendered_ordered_children")
def _rendered_ordered_children(obj, user, suffix=""):
    children = obj.ordered_content(user=user)
    return [
        mark_safe(select_template(get_template_names_for_obj(child, suffix)).render({"object": child}))
        for child in children
    ]
