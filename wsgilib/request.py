"""Request parsing."""

from flask import request
from werkzeug.local import LocalProxy

from functoolsplus import coerce


__all__ = ['ACCEPT', 'LANGUAGES']


@coerce(frozenset)
def _get_accept():
    """Yields accepting types."""

    accept = request.headers.get('Accept', '')
    return (item for item in accept.split(',') if item)


ACCEPT = LocalProxy(_get_accept)


class Language(str):
    """A language."""

    def __new__(cls, string, quality=None):
        return super().__new__(string)

    def __init__(self, _, quality=None):
        """Sets the quality."""
        super().__init__()
        self.quality = quality


@coerce(frozenset)
def _get_languages():
    """Returns the accepted languages."""

    languages = request.headers.get('Accept-Language', '').split(',')

    for language in languages:
        if language:
            try:
                language, quality = language.split(';')
            except ValueError:
                quality = None
            else:
                quality = float(quality[2:])

        yield Language(language, quality=quality)


LANGUAGES = LocalProxy(_get_languages)
