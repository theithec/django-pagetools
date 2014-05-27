import datetime
from django import template


# https://docs.djangoproject.com/en/dev/howto/custom-template-tags/
class CurrentTimeNode(template.Node):
    def __init__(self, format_string='%Y-%m-%d %I:%M %p'):
        self.format_string = format_string

    def render(self, context):
        return datetime.datetime.now().strftime(self.format_string)


def do_current_time(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, format_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0])
    if not (format_string[0] == format_string[-1] and
            format_string[0] in ('"', "'")):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % tag_name)
    return CurrentTimeNode(format_string[1:-1])
