"""Request parsing."""

from flask import request
from werkzeug.local import LocalProxy

from functoolsplus import coerce


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


@coerce(dict)
def _get_accept():
    """Yields accepting types."""

    accept = request.headers.get('Accept', '')

    for item in accept.split(','):
        if item:
            yield _split_quality(item)


ACCEPT = LocalProxy(_get_accept)


@coerce(dict)
def _get_languages():
    """Returns the accepted languages."""

    languages = request.headers.get('Accept-Language', '').split(',')

    for language in languages:
        if language:
            yield _split_quality(language)


LANGUAGES = LocalProxy(_get_languages)
