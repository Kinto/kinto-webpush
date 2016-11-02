import re
import requests

from kinto.core.utils import instance_uri
from six import iteritems


def on_resource_changed(event):
    """
    Everytime an object is created/changed/deleted, we update the
    bucket counters.

    If a new object exceeds the quotas, we reject the request.
    """
    payload = event.payload
    action = payload['action']
    resource_name = payload['resource_name']
    event_uri = payload['uri']

    permission = (action == "read") and "read" or "write"

    settings = event.request.registry.settings

    bucket_id = payload['bucket_id']
    bucket_uri = instance_uri(event.request, 'bucket', id=bucket_id)
    collection_id = None
    collection_uri = None
    if 'collection_id' in payload:
        collection_id = payload['collection_id']
        collection_uri = instance_uri(event.request,
                                      'collection',
                                      bucket_id=bucket_id,
                                      id=collection_id)

    storage = event.request.registry.storage

    # Get all subscriptions
    subscriptions, _ = storage.get_all('subscription', '*')
    import pdb; pdb.set_trace()
    for subscription in subscriptions:
        for pattern, permissions in iteritems(subscription['triggers']):
            pattern = re.compile('^%s$' % pattern.replace('*', '.*'))
            if collection_uri is not None:
                if pattern.match(collection_uri) and permission in permissions:
                    requests.post(subscription['push']['endpoint'])
            else:
                if pattern.match(bucket_uri) and permission in permissions:
                    requests.post(subscription['push']['endpoint'])
