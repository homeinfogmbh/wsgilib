"""Core application implementation."""

from contextlib import suppress
from traceback import format_exc, print_exc
from typing import Iterable, Union

from flask import Flask

from wsgilib.cors import CORS
from wsgilib.responses import Error, Response
from wsgilib.messages import JSONMessage, Message
from wsgilib.types import Route


__all__ = ['Application']


def dump_stracktrace() -> JSONMessage:
    """Dumps a stracktrace of an unexpected exception."""

    print('############################ cut here ############################')
    print_exc()
    print('######################## end of traceback ########################',
          flush=True)
    return JSONMessage('Internal server error.', status=500)


class Application(Flask):
    """Extended web application basis."""

    def __init__(self, *args, cors: Union[CORS, dict, bool] = None,
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
        return self._cors

    @cors.setter
    def cors(self, cors: Union[CORS, dict, bool]):
        """Sets the CORS settings."""
        if cors is True:
            self._cors = CORS()
        elif isinstance(cors, CORS):
            self._cors = cors
        elif cors:
            self._cors = CORS(cors)
        else:
            self._cors = None

    def _internal_server_error(self, _: Exception) -> Response:
        """Handles uncaught internal server errors."""
        if self.debug:
            return Error(format_exc(), status=500)

        return dump_stracktrace()

    def _postprocess_response(self, response: Response) -> Response:
        """Postprocesses the response."""
        if self.cors is not None:
            self.cors.apply(response.headers)

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
