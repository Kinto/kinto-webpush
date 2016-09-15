import pkg_resources
from kinto.core.events import ResourceChanged
from .listener import on_resource_changed

#: Module version, as defined in PEP-0396.
__version__ = pkg_resources.get_distribution(__package__).version


def includeme(config):
    # settings = config.get_settings()

    # Expose the capabilities in the root endpoint.
    message = "Register your WebPush endpoint to get notified on updates."
    docs = "https://github.com/Kinto/kinto-webpush"
    config.add_api_capability("webpush", message, docs, version=__version__)
    config.scan('kinto_webpush.views')

    # Listen to every resources
    config.add_subscriber(on_resource_changed, ResourceChanged,
                          for_resources=('bucket', 'group',
                                         'collection', 'record'))
