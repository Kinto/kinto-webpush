Kinto WebPush plugin
####################

Integration of Kinto with `WebPush
<https://tools.ietf.org/html/draft-ietf-webpush-protocol-02>`_, in order to
notify user agents of new changes.

|travis| |coveralls|

.. |travis| image:: https://travis-ci.org/Kinto/kinto-webpush.svg?branch=master
    :target: https://travis-ci.org/Kinto/kinto-webpush

.. |coveralls| image:: https://coveralls.io/repos/github/Kinto/kinto-webpush/badge.svg?branch=master
    :target: https://coveralls.io/github/Kinto/kinto-webpush?branch=master


Installation
============

In order to install the plugin, you need to first install it alongisde your
kinto instance::

 $ pip install kinto_webpush

And then include the plugin in your ``kinto.ini`` file::

  kinto.includes = kinto_webpush

It aims to implement the following blueprint: https://github.com/Kinto/kinto/wiki/WebHooks
