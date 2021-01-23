from django import template
from polls.models import Question


class LatestQuestionNode(template.Node):
    def render(self, context):
        qs = Question.objects.all().order_by("pub_date").reverse()
        if qs:
            q = qs[0]
            return '<a href="{url}">{text}</a>'.format(url=q.get_absolute_url(), text=q.question_text)
        return "No question available"
