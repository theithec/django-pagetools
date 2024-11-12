import sys

from demo_sections.models import Article, Section, SectionList
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import management
from django.core.management.base import BaseCommand
from django.utils import timezone
from filebrowser.base import FileObject
from polls.models import Question  # noqa

from pagetools.menus.models import AutoPopulated, Menu, ViewLink  # noqa
from pagetools.pages.models import Page  # noqa
from pagetools.settings import STATUS_PUBLISHED
from pagetools.widgets.models import ContentWidget  # noqa
from pagetools.widgets.models import (  # noqa
    PageType,
    TemplateTagWidget,
    TypeArea,
    WidgetInArea,
)


def create():
    site = Site.objects.first()
    site.domain = "127.0.0.1:8000"
    site.name = "Localhost"
    site.save()
    menu = Menu.objects.add_root("MainMenu")

    pagetype_base = PageType.objects.create(name="base")
    pagetype_special = PageType.objects.create(name="special")

    about_kwargs = {"pagetype": pagetype_special, "included_form": "Contactform"}
    pages_data = [
        ("Welcome", "start", "This is the start page"),
        ("About", "about", "More information. And a form.", about_kwargs),
    ]

    for data in pages_data:
        kwargs = data[3] if len(data) > 3 else {}
        page = Page.objects.get_or_create(
            title=data[0], slug=data[1], content=data[2], status=STATUS_PUBLISHED, **kwargs
        )[0]
        menu.children.add_child(page, enabled=True)

    typearea_base = TypeArea.objects.create(area="sidebar", pagetype=pagetype_base)
    typearea_special = TypeArea.objects.create(area="sidebar", pagetype=pagetype_special)

    content_widget1 = ContentWidget.objects.create(title="Widget1", name="widget1", content="I'm for base")
    content_widget2 = ContentWidget.objects.create(title="Widget2", name="widget2", content="I'm special")
    content_widget3 = ContentWidget.objects.create(title="Widget3", name="widget3", content="I'm always there")
    management.call_command("mk_templatetagwidgets")
    latest_question_widget = TemplateTagWidget.objects.get(name="latest_question")
    latest_question_widget.title = "Latest Questions"
    latest_question_widget.save()
    subscribe_widget = TemplateTagWidget.objects.get(name="subscribe")

    widgets_areas = (
        (content_widget1, typearea_base),
        (content_widget2, typearea_special),
        (content_widget3, typearea_base),
        (content_widget3, typearea_special),
        (latest_question_widget, typearea_base),
        (subscribe_widget, typearea_base),
    )
    for data in widgets_areas:
        WidgetInArea.objects.create(typearea=data[1], content_object=data[0], position=0, enabled=True)

    questions_data = (
        (
            "What's up?",
            ["A lot", "Even more"],
        ),
        (
            "What should i ask?",
            ["Not sure", "Nothing"],
        ),
    )

    for data in questions_data:
        qst = Question.objects.create(question_text=data[0], pub_date=timezone.now())
        for choice in data[1]:
            qst.choice_set.create(choice_text=choice)
    auto = AutoPopulated.objects.create(name="All questions")
    menu.children.add_child(auto, enabled=True)

    sl1 = SectionList.objects.create(title="Sectionlist1", slug="sectionlist1", status=STATUS_PUBLISHED)
    menu.children.add_child(sl1, enabled=True, title="Sections")
    s1 = Section.objects.create(title="Section1", slug="section1", status=STATUS_PUBLISHED)
    s1.pagenodepos_set.create(position=1, content=s1, owner=sl1)

    for i in range(40):
        kwargs = {}
        if i < 39:
            kwargs["status"] = STATUS_PUBLISHED
        a = Article.objects.create(
            title="Article %s" % i,
            content="Long version of article %s" % i,
            teaser="Short version of article %s" % i,
            image=FileObject("uploads/pic_10.jpg"),
            slug="article%s" % i,
            **kwargs,
        )
        a.pagenodepos_set.create(position=i, content=a, owner=s1)

    vl_polls = ViewLink.objects.create(title="Polls", name="polls:index")
    menu.children.add_child(vl_polls, enabled=True, title="Polls")
    articles_viewlink = ViewLink.objects.create(title="Articles", name="articles")
    menu.children.add_child(articles_viewlink, enabled=True, title="Paginated Articles")


class Command(BaseCommand):
    help = "Creates data for the pagetools demo"

    def handle(self, *args, **options):
        management.call_command("migrate")
        try:
            User.objects.create_superuser("admin", "q@w.de", "password")
        except BaseException:
            sys.exit("Error. DB exists?")
        create()
