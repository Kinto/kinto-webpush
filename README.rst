Kinto WebPush plugin
####################

Integration of Kinto with `WebPush
<https://tools.ietf.org/html/draft-ietf-webpush-protocol-02>`_, in order to
notify user agents of new changes.

Installation
============

In order to install the plugin, you need to first install it alongisde your
kinto instance::

 $ pip install kinto_webpush

And then include the plugin in your ``kinto.ini`` file::

  kinto.includes = kinto_webpush

Then, clients can send their push URIs at
``/buckets/{id}/collections/{id}/webpush``, and each time an object changes,
the User-Agents will be notified. That's all!
