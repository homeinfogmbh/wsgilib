"""Request parsing."""

from flask import request
from werkzeug.local import LocalProxy


__all__ = ['ACCEPT']


def _split_quality(string):
    """Splits an optional quality parameter
    q=<float> from the provided string.
    """

    try:
        string, quality = string.split(';')
    except ValueError:
        quality = 1
    else:
        _, quality = quality.split('=')
        quality = float(quality)

    return (string, quality)


def _split_csv(string):
    """Yields the respective elements."""

    for item in string.split(','):
        if item:
            yield _split_quality(item)


def get_accept():
    """Yields accepting types."""

    return dict(_split_csv(request.headers.get('Accept', '')))


ACCEPT = LocalProxy(get_accept)
