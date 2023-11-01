import json
import time

import sseclient
import threading
import queue

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
        self.url = '/api/events?{}'.format('&'.join(args))
        self.session = session
        self.timeout = timeout
        self.retry = 3000 # Retry time in milliseconds
        self.client = None
        self.queue = queue.Queue()
        self.do_shutdown = False
        self.worker = threading.Thread(target=self.fetch_events)
        self.worker.setDaemon(True)
        self.worker.start()

    def get(self):
        try:
            val = self.queue.get(timeout=self.timeout)
            if isinstance(val, EventError):
                raise val.exception
            return val
        except queue.Empty:
            return EventTimeout()

    def fetch_events(self):
        while not self.do_shutdown:
            try:
                with self.session.data_request("GET", self.session.urlbase, self.url, stream=True) as stream:
                    self.client = sseclient.SSEClient(stream)
                    for sse_event in self.client.events():
                        if sse_event.event == 'curve_event':
                            event = CurveEvent(sse_event)
                        else:
                            event = DefaultEvent(sse_event)
                        if hasattr(event, 'id') and event.id in self.curve_cache:
                            event.curve = self.curve_cache[event.id]
                        self.queue.put(event)
                        if sse_event.retry is not None:
                            try:
                                self.retry = int(sse_event.retry)
                            except Exception:
                                pass
                        if self.do_shutdown:
                            break
                    # Session was closed by server/network, wait for retry before looping.
                    time.sleep(self.retry / 1000.0)
            except Exception as e:
                self.queue.put(EventError(e))
                break

    def close(self, timeout=1):
        self.do_shutdown = True
        if self.client is not None:
            self.client.close()
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
        self._raw_event = sse_event
        try:
            self.json_data = json.loads(sse_event.data)
        except Exception:
            self.json_data = None


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
