.. _connect:

Connect to the Wattsight API
============================

In order to work with WAPI, first create a session.
A session can be configured using a config file, or by providing
your client_id and client_secret to the ``wapi.Session`` class
(:class:`wapi.session.Session`).

You can get the required id and secret by creating an OAuth client
at https://auth.wattsight.com/account/oauth-clients (as explained
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
    session = wapi.Session(client_id='client id', client_secret='client secret')

Using a proxy
-------------
You can set a proxy in the config file ::

    [proxies]
    http = http://10.10.1.10:3128
    https = http://10.10.1.10:1080

When creating a :class:`wapi.session.Session`, you can specify arguments that will be passed to :class:`requests.Session.send` ::

    import wapi
    proxies = {
      'https': 'https://10.10.1.10:1080',
    }
    session = wapi.Session(client_id='client id', client_secret='client secret',
                           requests_params={'proxies': proxies})


.. _sample config file: https://github.com/wattsight/wapi-python/tree/master/sampleconfig.ini
.. _here: https://api.wattsight.com/#documentation
