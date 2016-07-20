from pyramid.config import Configurator

def includeme(config):
    config.include("cornice")
    config.scan("kinto_webpush.views")

def main(global_config, **settings):
    message = "Register your WebPush endpoint to get notified on updates."
    docs = "https://github.com/Kinto/kinto-webpush"
    config.add_api_capability("webpush", message, docs)
    config = Configurator(settings=settings)
    config.include(includeme)
    return config.make_wsgi_app()
