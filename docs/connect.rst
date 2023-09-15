.. _connect:

Connect to the Volue Insight API
============================

In order to work with WAPI, first create a session.
A session can be configured using a config file, or by providing
your client_id and client_secret to the ``wapi.Session`` class
(:class:`wapi.session.Session`).

You can get the required id and secret by creating an OAuth client
at https://auth.volueinsight.com/account/oauth-clients (as explained
`here`_ )

Using a config file
-------------------

First you have to create a config file `yourfilename.ini`. The simplest way
is to take the :download:`sample config file <../sampleconfig.ini>`
provided and insert your client_id and client_secret.
Store your file somewhere and refer to it when
establishing the connection to WAPI::

    import wapi
    config_file_path = 'path/to/your/configfile.ini'
    session = wapi.Session(config_file=config_file_path)



Directly using client ID and secret
-----------------------------------

You can also directly use your client ID and secret as input to
the :class:`~wapi.session.Session` class ::

    import wapi
    session = wapi.Session(client_id='client id', client_secret='client secret', timeout=300)

The timeout parameter is optional and defaults to 300 seconds.
This can also be set in the config file as seen in :download:`sample config file <../sampleconfig.ini>`

Using a proxy
-------------

The library responds to the standard proxy evironment variables
(https_proxy, etc.) if they are present.


.. _sample config file: https://github.com/wattsight/wapi-python/tree/master/sampleconfig.ini
.. _here: https://api.volueinsight.com/#documentation
