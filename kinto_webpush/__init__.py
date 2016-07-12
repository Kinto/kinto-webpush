def includeme(config):
    settings = config.get_settings()

    # Expose the capabilities in the root endpoint.
    message = "Register your WebPush endpoint to get notified on updates."
    docs = "https://github.com/Kinto/kinto-webpush"
    config.add_api_capability("webpush", message, docs)
    config.scan('kinto_webpush.views')
