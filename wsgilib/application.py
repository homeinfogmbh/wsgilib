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
from logging import basicConfig, getLogger
from traceback import format_exc

from flask import Flask

try:
    from flask_cors import CORS
except ImportError:
    basicConfig()
    getLogger().warning('flask_cors not installed. CORS unavailable.')

from wsgilib.responses import Response, InternalServerError


__all__ = ['Application']


class Application(Flask):
    """Extended web application basis."""

    def __init__(self, *args, cors=None, debug=False, errorhandlers=(),
                 **kwargs):
        """Invokes super constructor and adds exception handlers."""
        super().__init__(*args, **kwargs)

        for exception, function in errorhandlers:
            self.errorhandler(exception)(function)

        self.errorhandler(Response)(lambda response: response)

        if debug:
            self.errorhandler(Exception)(lambda _: InternalServerError(
                msg=format_exc()))

        if cors:
            if cors is True:
                CORS(self)
            else:
                CORS(self, **cors)

    def add_routes(self, routes):
        """Adds the respective routes."""
        for methods, route, function, endpoint in routes:
            with suppress(AttributeError):
                methods = methods.split()

            self.add_url_rule(route, endpoint, function, methods=methods)
