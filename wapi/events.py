import json
import sseclient
import threading
import queue
import socket
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from . import curves, util
from builtins import str


class EventListener:
    def __init__(self, session, curve_list, start_time=None, timeout=None):
        self.curve_cache = {}
        ids = []
        if not hasattr(curve_list, '__iter__') or isinstance(curve_list, str):
            curve_list = [curve_list]
        for curve in curve_list:
            if isinstance(curve, curves.BaseCurve):
                ids.append(curve.id)
                self.curve_cache[curve.id] = curve
            else:
                ids.append(curve)
        args = [util.make_arg('id', ids)]
        if start_time is not None:
            args.append(util.make_arg('start_time', start_time))
        url = urljoin(session.urlbase, '/api/events?{}'.format('&'.join(args)))
        self.client = SSEClientWithAuth(url, session=session._session, auth=session.auth)
        self.timeout = timeout
        self.queue = queue.Queue()
        self.do_shutdown = False
        self.worker = threading.Thread(target=self.fetch_events)
        self.worker.setDaemon(True)
        self.worker.start()

    def get(self):
        try:
            val = self.queue.get(timeout=self.timeout)
            if isinstance(val, EventError):
                raise StopIteration()
            return val
        except queue.Empty:
            return EventTimeout()

    def fetch_events(self):
        while not self.do_shutdown:
            try:
                sse_event = next(self.client)
                if sse_event.event == 'curve_event' or sse_event.event == 'message':
                    event = CurveEvent(sse_event)
                else:
                    event = DefaultEvent(sse_event)
                if hasattr(event, 'id') and event.id in self.curve_cache:
                    event.curve = self.curve_cache[event.id]
                self.queue.put(event)
            except Exception as e:
                self.queue.put(EventError(e))
                break

    def close(self, timeout=1):
        self.do_shutdown = True
        try:
            self.client.close()
        except:
            raise
        self.worker.join(timeout)

    def __iter__(self):
        return self

    def __next__(self):
        return self.get()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class EventError:
    def __init__(self, exception):
        self.exception = exception

    def __str__(self):
        return "{}".format(self.exception)


class EventTimeout:
    """Returned on timeout, etc."""
    pass


class DefaultEvent(object):
    def __init__(self, sse_event):
        self.json_data = json.loads(sse_event.data)


class CurveEvent(DefaultEvent):
    def __init__(self, sse_event):
        super(CurveEvent, self).__init__(sse_event)
        self.id = self.json_data['id']
        self.curve = None
        self.created = util.parsetime(self.json_data['created'])
        self.operation = self.json_data['operation']
        self.tag = None
        self.issue_date = None
        self.range = None
        if 'tag' in self.json_data:
            self.tag = self.json_data['tag']
        if 'issue_date' in self.json_data:
            self.issue_date = util.parsetime(self.json_data['issue_date'])
        if 'range' in self.json_data:
            self.range = util.parserange(self.json_data['range'])


class SSEClientWithAuth(sseclient.SSEClient):
    def __init__(self, url, last_id=None, retry=3000, session=None, auth=None, **kwargs):
        self.auth = auth
        self.do_shutdown = False
        super(SSEClientWithAuth, self).__init__(url, last_id, retry, session, **kwargs)

    def _connect(self):
        if self.do_shutdown:
            raise StopIteration()
        if self.auth is not None:
            self.auth.validate_auth()
            headers = self.auth.get_headers(None)
            self.requests_kwargs['headers'].update(headers)
        super(SSEClientWithAuth, self)._connect()

    def close(self):
        """Attempt to close a hanging request forcibly, typically called from another thread."""
        self.do_shutdown = True
        try:
            # This is ugly, things are wrapped way too deep, this is the
            # most common pattern seen.
            self.resp.raw._fp.fp.raw._sock.shutdown(socket.SHUT_RDWR)
            self.resp.raw._fp.fp.raw._sock.close()
        except:
            pass
