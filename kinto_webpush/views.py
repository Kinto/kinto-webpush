from __future__ import print_function
from kinto.core import resource
import colander


# Validator
def trigger_valid(node, mapping):
    print(mapping)
    for key in mapping.keys():
        parts = key.split('/')
        if parts[0] != '' or parts[1] != 'buckets':
            raise colander.Invalid(node,
                                   "Trigger should start with `/buckets`."
                                   " Got %s" % key)

        if len(parts) < 4:
            # This is a valid bucket.
            break

        elif len(parts) < 6:
            if parts[3] in ('collections', 'groups'):
                # This is a valid collection or group.
                break
        elif len(parts) < 8:
            if parts[3] == 'collections' and parts[5] == "records":
                # This is a valid record.
                break

        raise colander.Invalid(node, "Trigger key %s is invalid." % key)

    for value in list(mapping.values())[0]:
        if value not in ('read', 'write'):
            raise colander.Invalid(node,
                                   "%s is not a valid permission "
                                   "to monitor" % value)


# Defining the schema
class KeySchema(colander.MappingSchema):
    auth = colander.SchemaNode(colander.String())
    p256dh = colander.SchemaNode(colander.String())


class PushSchema(colander.MappingSchema):
    endpoint = colander.SchemaNode(colander.String(), validator=colander.url)
    keys = KeySchema()


class SubscriptionSchema(resource.ResourceSchema):
    push = PushSchema()
    triggers = colander.SchemaNode(colander.Mapping(unknown='preserve'),
                                   validator=trigger_valid)


# Registering the resource.
@resource.register(name='subscription',
                   collection_path='/notifications/webpush',
                   record_path='/notifications/webpush/{{id}}')
class Subscription(resource.UserResource):
    mapping = SubscriptionSchema()
