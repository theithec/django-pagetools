import os
import sys
import django



from django.conf import settings
from django.test.utils import get_runner

def runtests():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    #sys.path.insert(0, 'demo')
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["pagetools"])
    sys.exit(bool(failures))

if __name__ == '__main__':
    runtests()
