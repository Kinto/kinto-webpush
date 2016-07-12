from kinto.core import Service

webpush = Service(name='webpush',
                  description='Handle webpush notification',
                  path='/notifications/webpush')

@webpush.get()
def webpush_get(request):
    return {}
