
from kinto.tests.core.support import unittest

from . import BaseWebTest


class HelloViewTest(BaseWebTest, unittest.TestCase):
    def test_capability_is_exposed(self):
        resp = self.app.get("/")
        capabilities = resp.json["capabilities"]
        self.assertIn("webpush", capabilities)
        expected = {
            "description": ("Register your WebPush endpoint "
                            "to get notified on updates."),
            "url": "https://github.com/Kinto/kinto-webpush",

        }
        self.assertEqual(expected, capabilities["webpush"])
