"""Core application implementation."""

from contextlib import suppress
from traceback import format_exc
from typing import Iterable, Union

from flask import Flask

from wsgilib.cors import CORS
from wsgilib.responses import Response
from wsgilib.messages import Message
from wsgilib.types import Route


__all__ = ['Application']


class Application(Flask):
    """Extended web application basis."""

    def __init__(self, *args, cors: Union[bool, dict] = None,
                 debug: bool = False, **kwargs):
        """Invokes super constructor and adds exception handlers."""
        super().__init__(*args, **kwargs)
        self.register_error_handler(Response, lambda response: response)
        self.register_error_handler(Message, lambda message: message)
        self.register_error_handler(Exception, self._internal_server_error)

        if cors is True:
            self.cors = CORS()
        elif cors:
            self.cors = CORS(cors)
        else:
            self.cors = None

        self.debug = debug
        self.after_request(self._postprocess_response)

    def _internal_server_error(self, exception: Exception) -> Response:
        """Handles uncaught internal server errors."""
        if self.debug:
            return (format_exc(), 500)

        return (str(exception), 500)

    def _postprocess_response(self, response: Response) -> Response:
        """Postprocesses the response."""
        if self.cors is not None:
            print('DEBUG:', 'Applying CORS', flush=True)
            self.cors.apply(response.headers)

        print('Resonse:', response, flush=True)
        return response

    def add_route(self, route: Route, strict_slashes: bool = False):
        """Adds the respective route."""
        methods, route, function = route

        with suppress(AttributeError):
            methods = methods.split()

        self.add_url_rule(
            route, f'{methods} {route}', function, methods=methods,
            strict_slashes=strict_slashes)

    def add_routes(self, routes: Iterable[Route],
                   strict_slashes: bool = False):
        """Adds the respective routes."""
        for route in routes:
            self.add_route(route, strict_slashes=strict_slashes)
