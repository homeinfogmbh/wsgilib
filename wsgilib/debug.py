"""Debugging tools."""

from sys import stderr
from traceback import print_exc

from wsgilib.messages import JSONMessage


__all__ = ['dump_stacktrace']


def dump_stacktrace() -> JSONMessage:
    """Dumps a stacktrace of an unexpected exception."""

    print('############################ cut here ############################',
          file=stderr)
    print_exc(file=stderr)
    print('######################## end of traceback ########################',
          file=stderr, flush=True)
    return JSONMessage('Internal server error.', status=500)
