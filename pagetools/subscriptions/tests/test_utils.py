from django.test.testcases import TestCase

from pagetools.subscriptions.models import Subscriber, QueuedEmail, SendStatus
from pagetools.subscriptions.utils import to_queue, send_max


class TC1Tests(TestCase):

    def setUp(self):
        for e in ('q@w.com', 'w@q.de', 'WW@qq.com'):
            Subscriber.objects.create(email=e, is_activated=True)
        to_queue({'title': 'Title', 'body': 'Content', })
        to_queue({'title': 'Title2', 'body': 'Content2', })

    def test_queues(self):
        self.assertEqual(len(QueuedEmail.objects.all()), 2)
        self.assertEqual(len(SendStatus.objects.all()), 6)

    def test_send(self):
        send_max()