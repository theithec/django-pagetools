import os

from demo_sections.models import Article, Section, SectionList
from django.test import TestCase
from filebrowser.base import FileObject
from filebrowser.sites import site

from pagetools.sections.models import PageNodePos


class SectionsDataTestCase(TestCase):
    def setUp(self):
        self.sections = []
        self.articles = []
        for i in range(1, 3):
            section = Section.objects.create(
                title="Section%s" % i,
                headline="HL%s" % i,
                status="published",
            )
            self.sections.append(section)
            article = Article.objects.create(
                title="Title%s" % i,
                slug="slug%s" % i,
                content="Text%s" % i,
                teaser="Teaser%s" % i,
                image=FileObject(os.path.join(site.directory, "foo.jpg")),
                status="published",
            )
            self.articles.append(article)

        sec1, _ = self.sections
        PageNodePos.objects.create(content=self.articles[0], owner=sec1, position=0)
        self.sectionlist1 = SectionList.objects.create(
            title="Sectionlist1",
            slug="sectionlist1",
            status="published",
        )
        PageNodePos.objects.create(content=sec1, owner=self.sectionlist1, position=0)
