from cliquet import resource
import colander


_parent_path = '/buckets/{{bucket_id}}/collections/{{collection_id}}'

class WebPushSchema(resource.ResourceSchema):
    # XXX Should be an URL.
    url = colander.SchemaNode(colander.String())


@resource.register(collection_path=_parent_path + '/webpush',
                   record_path=_parent_path + '/webpush/{{id}}')
class WebPush(resource.UserResource):
    mapping = WebPushSchema()

    def get_parent_id(self, request):
        bucket_id = request.matchdict['bucket_id']
        if bucket_id == 'default':
            bucket_id = request.default_bucket_id
        collection_id = request.matchdict['collection_id']
        return '/buckets/%s/collections/%s' % (bucket_id,
                                               collection_id)
