# python-wapi
Wattsight API python library

This library is meant as a simple toolkit for working with data from
https://data.mkonline.com/ (or equivalent services).  Note that access
is based on some sort of login credentials, this library is not all
that useful unless you have a valid MKonline account.

class:

Session -- Main access point, handling the connection to the data library.

    methods:

    __init__(host=None, config_file=None):
        Create the connection object to work with the data service.

        When `host' is given, it will override the default host part
        of the urls used, and also override any host name given in
        the config_file.

        When `config_file' is given, it should be the path to an
        ini-style file containing access configuration parameters.

    configure(config_file)
        Explicit call to the configuration file reading, usually
        only called implicitly from __init__.  Note that if you call
        configure explicitly and the host is specified in the
        configuration file, it will override any host supplied in
        the __init__ call.  Re-configuring a session is not supported.

    get_curve(id=None, name=None)
        Get a curve object of the correct type for a given curve id or name.
        Either id or name must be given, if both are, name is ignored.
        This returns the metadata about the curve, further calls exist
        on each curve type to work with the data itself.

    search(**kw)
        Run a search on the backend.  Any keyword argument supplied is
        converted into a corresponding search term, the resulting search
        is for all terms.  A keyword argument containing a list of values
        will search for any of those values for that key.

    make_curve(id, type)
        Build a curve object with only id, it can be used when the metadata
        is not needed, or not available through regular means.  Type should be
        one of TIME_SERIES, TAGGED, INSTANCES or TAGGED_INSTANCES.

    events(curve_list)
        Return an object listening for changes on the supplied curves
        (a list of curve objects or ids).  Each call to the get
        method of of this object will wait until something happens, and
        then return a change dictionary.  This dictionary contains the
        'id', the timestamp of the event ('created'), what was
        done ('operation') and optionally the tag, issue_date and range
        information of the curve that was changed.  If the event listener
        is created using curve objects, it will be returned as 'curve'.

    get_attribute(attribute)
        Return a list of possible values for the given attribute.
