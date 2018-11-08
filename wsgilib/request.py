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


def get_accept():
    """Yields accepting types."""

    return _AcceptDict(_split_csv(request.headers.get('Accept', '')))


ACCEPT = LocalProxy(get_accept)


def get_languages():
    """Returns the accepted languages."""

    return dict(_split_csv(request.headers.get('Accept-Language', '')))


LANGUAGES = LocalProxy(get_languages)


class _AcceptDict(dict):
    """Stores MIME types and a corresponding quality
    parameter representing the "Accept:" headers.
    """

    def __contains__(self, item):
        """Checks whether the respective MIME type is supported.
        This is the case if it is explicitely sent or any MIME
        type ("*/*") is supported.
        """
        return super().__contains__(item) or super().__contains__('*/*')
