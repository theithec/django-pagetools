from django.apps import AppConfig
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify

from django.db.models.signals import post_save

from django.dispatch import receiver


# This will be added later to ``polls.models.Question``
def question_get_absolute_url(self):
    return reverse("polls:detail", args=(self.pk,))


# Notify subscribers about new questions
@receiver(post_save)
def questions_post_savecallback(sender, **kwargs):
    from pagetools.subscriptions.utils import to_queue

    if sender.__name__ == "Question" and kwargs["created"] == True:
        to_queue(
            {
                "title": "New Question",
                "body": "There is a great new question: %s." % (kwargs["instance"].question_text),
            }
        )


class MainConfig(AppConfig):
    name = "main"

    def ready(self):
        import polls.admin
        from polls.views import DetailView
        from polls.models import Question

        from pagetools.menus.models import MenuEntry
        from pagetools.menus.utils import (
            entrieable_auto_populated,
            entrieable_reverse_name,
        )
        from pagetools.menus.admin import make_entrieable_admin
        from pagetools.pages.models import Page
        import pagetools.search

        # To enable questions to be added easily to a menu, tweak their admin:
        make_entrieable_admin(polls.admin.QuestionAdmin)

        # But ...
        # A content_object in a `MenuEntry` needs `get_absolute_url`,
        # so add one to ``Question``.
        Question.add_to_class("get_absolute_url", question_get_absolute_url)
        # And make a menukey available for highlighting the active menuentry 
        Question.add_to_class("get_menukey", lambda q: "question:" + slugify(q))


        # For a dynamic menu entry with all questions as children
        # we need a function to define the dynamic entries:
        def recent_questions_as_entries():
            return [
                MenuEntry(title=q.question_text, content_object=q)
                for q in Question.objects.filter(pub_date__lte=timezone.now())
            ]

        # tell pagetools menus about it
        entrieable_auto_populated("All questions", recent_questions_as_entries)

        # Add "polls:index" as menu entry
        # entrieable_reverse_name("index", app_name="polls")
        # or
        entrieable_reverse_name("polls:index")

        # Give the polls detail view another pagetype:
        DetailView.pagetype_name = "special"

        # Make Questions searchable
        pagetools.search.search_mods = (
            (Question, ("question_text",)),
            # and pages also
            (Page, ("title", "content"), {"replacements": "content"}),
        )
