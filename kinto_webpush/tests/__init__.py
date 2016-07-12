import os

import webtest
from kinto.tests.core import support as core_support

class BaseWebTest(object):
    config = '../../webpush.ini'

    def __init__(self, *args, **kwargs):
        super(BaseWebTest, self).__init__(*args, **kwargs)
        self.app = self.make_app()


    def make_app(self):
        curdir = os.path.dirname(os.path.realpath(__file__))
        app = webtest.TestApp("config:%s" % self.config, relative_to=curdir)
        app.RequestClass = core_support.get_request_class(prefix="v1")

        return app
