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


def _dict_from_csv(string):
    """Returns a dict from comma separated values."""

    return {
        key: value for key, value in _split_quality(item)
        for item in string.split(',') if item}


def get_accept():
    """Yields accepting types."""

    return _dict_from_csv(request.headers.get('Accept', ''))


ACCEPT = LocalProxy(get_accept)


def get_languages():
    """Returns the accepted languages."""

    return _dict_from_csv(request.headers.get('Accept-Language', ''))


LANGUAGES = LocalProxy(get_languages)
