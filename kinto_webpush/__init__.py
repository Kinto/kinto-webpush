import copy

from cliquet.events import ResourceChanged
from kinto import authorization
from pyramid.security import IAuthorizationPolicy
from zope.interface import implementer

INHERITANCE_TREE = copy.deepcopy(authorization.PERMISSIONS_INHERITANCE_TREE)
INHERITANCE_TREE['collection:webpush:create'] = {
    'webpush': ['read', 'write']
}

for key in INHERITANCE_TREE.keys():
    if key.startswith(('collection:', 'records:')):
        INHERITANCE_TREE[key]['webpush'] = ['write']


@implementer(IAuthorizationPolicy)
class AuthorizationPolicy(authorization.AuthorizationPolicy):
    def get_bound_permissions(self, *args, **kwargs):

        return authorization.build_permissions_set(
            inheritance_tree=INHERITANCE_TREE,
            *args, **kwargs)


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
            recipients = event.request.storage.get_all(
                collection_id=parent_id + "/webpush",
                parent_id=parent_id)
            
            from pdb import set_trace; set_trace()

    config.add_subscriber(on_resource_changed, ResourceChanged)
    config.scan('kinto_webpush.views')

