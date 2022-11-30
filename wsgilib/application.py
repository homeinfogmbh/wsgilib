"""Core application implementation."""

from traceback import format_exc
from typing import Iterable, Optional

from flask import Flask

from wsgilib.cors import CORS
from wsgilib.debug import dump_stacktrace
from wsgilib.responses import Error, Response
from wsgilib.messages import Message
from wsgilib.types import CORSType, RouteType


__all__ = ['Application']


class Application(Flask):
    """Extended web application basis."""

    def __init__(self, *args, cors: Optional[CORSType] = None,
                 debug: bool = False, **kwargs):
        """Invokes super constructor and adds exception handlers."""
        super().__init__(*args, **kwargs)
        self.register_error_handler(Response, lambda response: response)
        self.register_error_handler(Message, lambda message: message)
        self.register_error_handler(Exception, self._internal_server_error)
        self.after_request(self._postprocess_response)
        self.cors = cors
        self.debug = debug

    @property
    def cors(self):
        """Returns the CORS settings."""
        if self._cors is None:
            return None

        if self._cors is True:
            return CORS()

        if isinstance(self._cors, CORS):
            return self._cors

        if callable(self._cors):
            return CORS(self._cors())

        return CORS(self._cors)

    @cors.setter
    def cors(self, cors: CORSType):
        """Sets the CORS settings."""
        self._cors = cors

    def _internal_server_error(self, _: Exception) -> Response:
        """Handles uncaught internal server errors."""
        if self.debug:
            return Error(format_exc(), status=500)

        return dump_stacktrace()

    def _postprocess_response(self, response: Response) -> Response:
        """Post-processes the response."""
        if self.cors is not None:
            self.cors.apply(response.headers)

        return response

    def add_route(self, route: RouteType, strict_slashes: bool = False):
        """Adds the respective route."""
        try:
            methods, route, function, endpoint = route
        except ValueError:
            methods, route, function = route
            endpoint = f'{methods} {route}'

        if isinstance(methods, str):
            methods = methods.split()

        self.add_url_rule(
            route, endpoint, function, methods=methods,
            strict_slashes=strict_slashes)

    def add_routes(self, routes: Iterable[RouteType],
                   strict_slashes: bool = False):
        """Adds the respective routes."""
        for route in routes:
            self.add_route(route, strict_slashes=strict_slashes)

    def register_error_handlers(self, error_handlers: dict) -> None:
        """Add multiple error handlers."""
        for exception, handler in error_handlers.items():
            self.register_error_handler(exception, handler)
