import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def runtests():
    os.environ["DJANGO_SETTINGS_MODULE"] = "demo.settings.tests"
    sys.path.append("./demo")
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(failfast=False)
    failures = test_runner.run_tests(["pagetools", "polls", "demo_sections"])
    sys.exit(bool(failures))


if __name__ == "__main__":
    runtests()
