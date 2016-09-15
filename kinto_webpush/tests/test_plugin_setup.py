import unittest

from kinto_webpush import __version__ as webpush_version
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
            "version": webpush_version
        }
        self.assertEqual(expected, capabilities["webpush"])
