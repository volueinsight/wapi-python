#
# Wattsight API access library
#
import os
from .session import Session
from . import auth, curves, events, session, util

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'VERSION')) as fv:
    VERSION = __version__ = fv.read().strip()
