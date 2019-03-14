"""Web application messaging."""

from wsgilib.responses import JSON


__all__ = ['Message', 'JSONMessage']


class Message(Exception):
    """Base class for messages."""


class JSONMessage(Message):
    """Base class for messages returned
    or raised by a web application.
    """

    def __init__(self, message, status=200, **fields):
        """Sets message ID and status."""
        super().__init__()
        self.message = message
        self.status = status
        self.fields = fields

    def __call__(self, environ, start_response):
        """Implements the flask.Response interface."""
        return JSON(self.dictionary, status=self.status)

    @property
    def dictionary(self):
        """Returns the JSON dictionary."""
        dictionary = dict(self.fields)
        dictionary['message'] = self.message
        return dictionary

    def update(self, message=None, **fields):
        """Updates the extra dictionary fields."""
        new_fields = dict(self.fields)
        new_fields.update(fields)
        message = self.message if message is None else message
        return type(self)(message, status=self.status, **fields)
