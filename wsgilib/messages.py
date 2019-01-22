"""Web application messaging."""

from functools import lru_cache
from gettext import translation
from operator import itemgetter

from wsgilib.request import LANGUAGES
from wsgilib.responses import JSON


__all__ = ['LanguageNotFound', 'Message']


LOCALES_DIR = '/usr/local/etc/his.d/locales'
FALLBACK_LANG = {'de_DE': 0.1}


class LanguageNotFound(Exception):
    """Indicates that the respective language could not be found."""

    def __init__(self, lang):
        """Sets the respective language."""
        super().__init__(lang)
        self.lang = lang


@lru_cache()
def get_locales(basedir, domain):
    """Returns the fist best locale."""

    languages = dict(FALLBACK_LANG)
    languages.update(dict(LANGUAGES))
    languages = sorted(languages.items(), key=itemgetter(1), reverse=True)
    languages = [language for language, _ in languages]

    try:
        return translation(domain, basedir, languages)
    except FileNotFoundError:
        raise LanguageNotFound(languages)


class Message:
    """Base class for messages returned by a web application."""

    BASEDIR = NotImplemented
    DOMAIN = NotImplemented

    def __init__(self, msgid, status=200, *,
                 localized_message=None, fields=None):
        """Sets message ID and status."""
        self.msgid = msgid
        self.status = status
        self._localized_message = localized_message
        self.fields = fields or {}

    def __call__(self, environ, start_response):
        """Implements the flask.Response interface."""
        return self.response(environ, start_response)

    @property
    def locales(self):
        """Returns the respective locales."""
        return get_locales(type(self).BASEDIR, type(self).DOMAIN)

    @property
    def localized_message(self):
        """Returns a message with currently set locales."""
        if self._localized_message is None:
            return self.locales.gettext(self.msgid)

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
            self.msgid, status=self.status,
            localized_message=localized_message, fields=self.fields)

    def update(self, *dicts, status=None, **kwargs):
        """Updates the extra dictionary fields."""
        fields = dict(self.fields)

        for dictionary in dicts:
            fields.update(dictionary)

        status = self.status if status is None else status
        fields.update(kwargs)
        return type(self)(
            self.msgid, status=status,
            localized_message=self._localized_message, fields=fields)
