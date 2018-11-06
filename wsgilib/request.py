"""Request parsing."""

from flask import request
from werkzeug.local import LocalProxy

from functoolsplus import coerce


__all__ = ['ACCEPT', 'LANGUAGES']


@coerce(frozenset)
def _get_accept():
    """Yields accepting types."""

    accept = request.headers.get('Accept', '')

    for item in accept.split(','):
        if item:
            yield QualityString.from_string(item)


ACCEPT = LocalProxy(_get_accept)


@coerce(frozenset)
def _get_languages():
    """Returns the accepted languages."""

    languages = request.headers.get('Accept-Language', '').split(',')

    for language in languages:
        if language:
            yield QualityString.from_string(language)


LANGUAGES = LocalProxy(_get_languages)


class QualityString(str):
    """A string with relative quality attribute."""

    def __new__(cls, string, quality=None):
        return super().__new__(cls, string)

    def __init__(self, _, quality=None):
        """Sets the quality."""
        super().__init__()
        self.quality = quality

    @classmethod
    def from_string(cls, string):
        """Creates the QualityString from the provided string."""
        try:
            string, quality = string.split(';')
        except ValueError:
            quality = None
        else:
            quality = float(quality[2:])

        return cls(string, quality=quality)
