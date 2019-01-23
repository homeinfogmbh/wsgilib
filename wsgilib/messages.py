"""Web application messaging."""

from functools import lru_cache
from gettext import translation
from operator import itemgetter
from pathlib import Path

from wsgilib.request import LANGUAGES
from wsgilib.responses import JSON


__all__ = ['LanguageNotFound', 'MessageFacility']


class LanguageNotFound(Exception):
    """Indicates that the respective language could not be found."""

    def __init__(self, lang):
        """Sets the respective language."""
        super().__init__(lang)
        self.lang = lang


class MessageFacility:
    """Manages a message base directory and domain."""

    def __init__(self, basedir):
        """Sets the base directory."""
        self.basedir = Path(basedir)

    def domain(self, name):
        """Returns a message domain."""
        return Domain(self, name)


class Domain:
    """Manages a message domain."""

    def __init__(self, facility, name, default=None):
        """Sets facility and name."""
        self.facility = facility
        self.name = name
        self.default = default

    @property
    def _basedir(self):
        """Returns the basedir as string."""
        return str(self.facility.basedir)

    @property
    @lru_cache()
    def locales(self):
        """Returns the fist best locale."""
        languages = dict(self.default) if self.default else {}
        languages.update(dict(LANGUAGES))
        languages = sorted(languages.items(), key=itemgetter(1), reverse=True)
        languages = [language for language, _ in languages]

        try:
            return translation(self.name, self._basedir, languages)
        except FileNotFoundError:
            raise LanguageNotFound(languages)

    def message(self, msgid, status=200):
        """Returns a new message for this domain."""
        return Message(self, msgid, status=status)


class Message(Exception):
    """Base class for messages returned
    or raised by a web application.
    """

    def __init__(self, domain, msgid, status=200, *,
                 localized_message=None, fields=None):
        """Sets message ID and status."""
        super().__init__()
        self.domain = domain
        self.msgid = msgid
        self.status = status
        self._localized_message = localized_message
        self.fields = fields or {}

    def __call__(self, environ, start_response):
        """Implements the flask.Response interface."""
        return self.response(environ, start_response)

    def __repr__(self):
        """Returns a human readable string representation of the message."""
        return '{}(msgid={}, status={})'.format(
            type(self), repr(self.msgid), repr(self.status))

    @property
    def localized_message(self):
        """Returns a message with currently set locales."""
        if self._localized_message is None:
            return self.domain.locales.gettext(self.msgid)

        return self._localized_message

    @property
    def dictionary(self):
        """Returns the appropriate JSON dictionary."""
        dictionary = {'message': self.localized_message}
        dictionary.update(self.fields)
        return dictionary

    @property
    def response(self):
        """Converts the message into a JSON response."""
        return JSON(self.dictionary, status=self.status)

    def format(self, *args, **kwargs):
        """Formats the message."""
        localized_message = self.localized_message.format(*args, **kwargs)
        return type(self)(
            self.domain, self.msgid, status=self.status,
            localized_message=localized_message, fields=self.fields)

    def update(self, *dicts, status=None, **kwargs):
        """Updates the extra dictionary fields."""
        fields = dict(self.fields)

        for dictionary in dicts:
            fields.update(dictionary)

        status = self.status if status is None else status
        fields.update(kwargs)
        return type(self)(
            self.domain, self.msgid, status=status,
            localized_message=self._localized_message, fields=fields)
