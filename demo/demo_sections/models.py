from django.db import models
from django.urls import reverse
from filebrowser.fields import FileBrowseField

from pagetools.sections.models import PageNode, PageNodeManager, TypeMixin


class Article(PageNode):
    content = models.TextField("Content")
    teaser = models.TextField("Teaser")
    image = FileBrowseField("Image", max_length=200)
    allowed_children_classes = [
        "demo_sections.models.Article",
    ]
    objects = PageNodeManager()

    def get_absolute_url(self):
        return reverse(
            "sections:node",
            kwargs={
                "slug": self.slug,
            },
        )


class Section(TypeMixin, PageNode):
    node_choices = (
        ("section_style1", "Style 1"),
        ("section_style2", "Style 2"),
    )
    headline = models.CharField("Headline", max_length=255)
    allowed_children_classes = [
        Article,
    ]
    objects = PageNodeManager()


class SectionList(PageNode):
    allowed_children_classes = [Section, Article]
    objects = PageNodeManager()

    class Meta:
        proxy = True
