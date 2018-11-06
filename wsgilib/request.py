"""Request parsing."""

from flask import request
from werkzeug.local import LocalProxy


__all__ = ['ACCEPT', 'LANGUAGES']


def _split_quality(string):
    """Splits an optional quality parameter
    q=<float> from the provided string.
    """

    try:
        string, quality = string.split(';')
    except ValueError:
        quality = 1
    else:
        quality = float(quality[2:])

    return (string, quality)


def _split_csv(string):
    """Yields the respective elements."""

    for item in string.split(','):
        if item:
            yield _split_quality(item)


def _csv_to_dict(string):
    """Returns a dict from comma separated values."""

    return dict(_split_csv(string))


def get_accept():
    """Yields accepting types."""

    return _csv_to_dict(request.headers.get('Accept', ''))


ACCEPT = LocalProxy(get_accept)


def get_languages():
    """Returns the accepted languages."""

    return _csv_to_dict(request.headers.get('Accept-Language', ''))


LANGUAGES = LocalProxy(get_languages)
