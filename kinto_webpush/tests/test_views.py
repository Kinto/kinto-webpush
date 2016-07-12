from kinto.tests.core.support import unittest

from . import BaseWebTest


class SubscriptionViewTest(BaseWebTest, unittest.TestCase):
    def test_user_can_list_their_subscriptions(self):
        resp = self.app.get("/notifications/webpush")
        
