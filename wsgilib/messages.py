"""Web application messaging."""

from __future__ import annotations
from typing import Callable

from wsgilib.responses import JSON


__all__ = ['Message', 'JSONMessage']


class Message(Exception):
    """Base class for messages."""

    def __call__(self, environ: dict, start_response: Callable):
        """Implements the flask.Response interface."""
        return self.response(environ, start_response)

    @property
    def response(self):
        """Returns a response object."""
        raise NotImplementedError()


class JSONMessage(Message):
    """Base class for messages returned
    or raised by a web application.
    """

    def __init__(self, message: str, status: int = 200, **fields):
        """Sets message ID and status."""
        super().__init__()
        self.message = message
        self.status = status
        self.fields = fields

    @property
    def json(self) -> dict:
        """Returns the JSON dictionary."""
        return {**self.fields, 'message': self.message}

    @property
    def response(self) -> JSON:
        """Returns a JSON response object."""
        return JSON(self.json, status=self.status)

    def update(self, message: str = None, status: int = None,
               **fields) -> JSONMessage:
        """Updates the extra dictionary fields."""
        fields = {**self.fields, **fields}
        message = self.message if message is None else message
        status = self.status if status is None else status
        return type(self)(message, status=status, **fields)
