import copy
import requests

from cliquet.events import ResourceChanged
from kinto import authorization


def includeme(config):
    def on_resource_changed(event):
        """On any event on the collection, see if there are registered WebPush
        URLs and notify them if there is.
        """
        resource_name = event.payload['resource_name']
        action = event.payload['action']

        collection_update = (resource_name == 'collection' and
                             action != "create")
        if collection_update or resource_name == "record":
            bucket_id = event.payload['bucket_id']
            collection_id = event.payload['collection_id']
            parent_id = "/buckets/%s/collections/%s" % (bucket_id, collection_id)

            # XXX Need to find a way to expire the URLs after some point,
            # otherwise they will just pile up and being pinged even if
            # useless.
            recipients, _ = event.request.registry.storage.get_all(
                collection_id="webpush", parent_id=parent_id)
            for recipient in recipients:
                requests.post(recipient['url'])

    config.add_subscriber(on_resource_changed, ResourceChanged)
    config.scan('kinto_webpush.views')

