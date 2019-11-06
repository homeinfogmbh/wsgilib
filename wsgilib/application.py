# Copyright 2017 HOMEINFO - Digitale Informationssysteme GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""Core application implementation."""

from contextlib import suppress
from traceback import format_exc
from uuid import uuid4

from flask import Flask

from wsgilib.cors import CORS
from wsgilib.responses import Response, InternalServerError
from wsgilib.messages import Message


__all__ = ['Application']


def _id(message):
    """Returns the message itself."""

    return message


class Application(Flask):
    """Extended web application basis."""

    def __init__(self, *args, cors=None, debug=False, errorhandlers=(),
                 **kwargs):
        """Invokes super constructor and adds exception handlers."""
        super().__init__(*args, **kwargs)

        for exception, function in errorhandlers:
            self.errorhandler(exception)(function)

        self.errorhandler(Response)(_id)
        self.errorhandler(Message)(_id)
        self.cors = CORS(cors) if cors else CORS()

        if debug:
            self.errorhandler(Exception)(lambda _: InternalServerError(
                msg=format_exc()))

        self.after_request(self.set_cors)

    def set_cors(self, response):
        """Sets the CORS headers on the response."""
        self.cors.apply(response.headers)
        return response

    def add_routes(self, routes, strict_slashes=False):
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
