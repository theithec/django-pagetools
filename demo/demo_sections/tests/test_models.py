from demo_sections.tests import SectionsDataTestCase

from pagetools.sections.utils import get_template_names_for_obj


class ModelsTest(SectionsDataTestCase):
    def test_article(self):
        self.assertEqual(self.articles[0].title, "Title1")
        self.assertEqual(self.sections[0].title, "Section1")

    def test_templatenames(self):
        template_names = get_template_names_for_obj(self.articles[0])
        self.assertListEqual(["sections/article-slug1.html", "sections/article.html"], template_names)
