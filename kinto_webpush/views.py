from cliquet import resource
import colander


_parent_path = '/buckets/{{bucket_id}}/collections/{{collection_id}}'

class WebPushSchema(resource.ResourceSchema):
    # XXX Should be an URL.
    url = colander.SchemaNode(colander.String())


@resource.register(collection_path=_parent_path + '/webpush',
                   record_path=_parent_path + '/webpush/{{id}}')
class WebPush(resource.ShareableResource):
    mapping = WebPushSchema()
