"""Core application implementation."""

from contextlib import suppress
from uuid import uuid4
from typing import Iterable

from flask import Flask

from wsgilib.cors import CORS
from wsgilib.responses import Response, InternalServerError
from wsgilib.messages import Message
from wsgilib.types import ErrorHandler, Route


__all__ = ['Application']


def internal_server_error(exception: Exception) -> InternalServerError:
    """Returns an internal server error."""

    return InternalServerError(msg=exception.with_traceback())


class Application(Flask):
    """Extended web application basis."""

    def __init__(self, *args, cors: bool = None, debug: bool = False,
                 errorhandlers: Iterable[ErrorHandler] = None, **kwargs):
        """Invokes super constructor and adds exception handlers."""
        super().__init__(*args, **kwargs)

        for exception, function in errorhandlers or ():
            self.errorhandler(exception)(function)

        self.errorhandler(Response)(lambda response: response)
        self.errorhandler(Message)(lambda message: message)

        if cors is True:
            self.cors = CORS()
        elif cors:
            self.cors = CORS(cors)
        else:
            self.cors = None

        if debug:
            self.errorhandler(Exception)(internal_server_error)

        self.after_request(self.set_cors)

    def set_cors(self, response: Response) -> Response:
        """Sets the CORS headers on the response."""
        if self.cors is not None:
            self.cors.apply(response.headers)

        return response

    def add_routes(self, routes: Iterable[Route],
                   strict_slashes: bool = False):
        """Adds the respective routes."""
        for route in routes:
            try:
                methods, route, function, endpoint = route
            except ValueError:
                methods, route, function = route
                endpoint = uuid4().hex

            with suppress(AttributeError):
                methods = methods.split()

            self.add_url_rule(
                route, endpoint, function, methods=methods,
                strict_slashes=strict_slashes)
