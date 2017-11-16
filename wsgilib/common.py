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
"""Simple (U)WSGI framework for web applications."""

from functools import lru_cache
from hashlib import sha256
from traceback import format_exc

from fancylog import LoggingClass
from mimeutil import mimetype
from pyxb import PyXBException
from strflib import latin2utf
from xmldom import DisabledValidation

from wsgilib.misc import HTTP_STATUS, strip_json, escape_object, \
    json_dumps, json_loads, query_to_dict

__all__ = [
    'Headers',
    'WsgiResponse',
    'Response',
    'Error',
    'PlainText',
    'OK',
    'HTML',
    'XML',
    'JSON',
    'Binary',
    'InternalServerError',
    'PostData',
    'RequestHandler',
    'WsgiApp']


class Headers:
    """Wraps response headers."""

    def __init__(self, content_type=None, content_length=None,
                 charset=None, cors=None, fields=None):
        """ Generates response headers."""
        self.content_type = content_type
        self.content_length = content_length
        self.charset = charset
        self.cors = cors
        self.fields = fields or {}

    def __iter__(self):
        """Yields header fields."""
        if self.content_type is not None:
            if self.charset is not None:
                charset = 'charset={}'.format(self.charset)
                content_type = '{};{}'.format(self.content_type, charset)
            else:
                content_type = self.content_type

            yield ('Content-Type', content_type)

        if self.content_length is not None:
            yield ('Content-Length', str(self.content_length))

        # Cross-origin resource sharing.
        if self.cors:
            try:
                origin, methods = self.cors
            except (ValueError, TypeError):
                origin = self.cors
                methods = ['GET', 'POST', 'DELETE', 'PUT', 'PATCH']

            if origin is True:
                yield ('Access-Control-Allow-Origin', '*')
            else:
                yield ('Access-Control-Allow-Origin', str(origin))

            if methods:
                methods = ', '.join(m.upper() for m in methods)
                yield ('Access-Control-Allow-Methods', methods)

        # User-defined fields.
        yield from self.fields.items()


class WsgiResponse:
    """A WSGI response."""

    def __init__(self, status, content_type=None, response_body=None,
                 charset=None, cors=None, headers=None):
        """Creates a generic WSGI response"""
        self.status = (status, HTTP_STATUS[status])

        try:
            content_length = len(response_body)
        except TypeError:
            content_length = None

        self.headers = Headers(
            content_type, content_length, charset=charset, cors=cors,
            fields=headers)
        self.response_body = response_body

    def __iter__(self):
        """Yields response fields."""
        yield '{} {}'.format(*self.status)
        # Headers must be a list at this point
        yield list(self.headers)
        yield self.response_body

    @property
    def cors(self):
        """Returns the CORS settings."""
        return self.headers.cors

    @cors.setter
    def cors(self, cors):
        """Fixes CORS settings on the respective response."""
        if self.headers.cors is None:
            self.headers.cors = cors


class Response(Exception, WsgiResponse):
    """An WSGI error message."""

    def __init__(self, msg=None, status=200, content_type='text/plain',
                 charset='utf-8', encoding=True, cors=None, headers=None):
        """Generates an error WSGI response."""
        if msg is not None:
            if encoding is True:
                encoding = charset

            if encoding:
                msg = msg.encode(encoding=charset)

        Exception.__init__(self, msg)
        WsgiResponse.__init__(
            self, status, content_type=content_type, response_body=msg,
            charset=charset, cors=cors, headers=headers)


class PlainText(Response):
    """Returns a successful plain text response."""

    def __init__(self, msg=None, status=200, charset='utf-8', cors=None):
        """Returns a plain text success response."""
        super().__init__(
            msg=msg, status=status, content_type='text/plain',
            charset=charset, encoding=True, cors=cors)


class Error(PlainText):
    """An WSGI error message."""

    def __init__(self, msg=None, status=400, charset='utf-8', cors=None):
        """Returns a plain text error response."""
        if 400 <= status < 600:
            super().__init__(
                msg=msg, status=status, charset=charset, cors=cors)
        else:
            raise ValueError('Not an error status: {}'.format(status))


class OK(PlainText):
    """Returns a successful plain text response."""

    def __init__(self, msg=None, status=200, charset='utf-8', cors=None):
        """Returns a plain text success response."""
        if 200 <= status < 300:
            super().__init__(
                msg=msg, status=status, charset=charset, cors=cors)
        else:
            raise ValueError('Not a success status: {}'.format(status))


class HTML(Response):
    """Returns a successful plain text response."""

    def __init__(self, msg=None, status=200, charset='utf-8', cors=None):
        """Returns a plain text success response."""
        super().__init__(
            msg=msg, status=status, content_type='text/html',
            charset=charset, encoding=True, cors=cors)


class XML(Response):
    """An XML response."""

    def __init__(self, dom, validate=True, status=200, charset='utf-8',
                 cors=None):
        """Sets the dom and inherited responde attributes."""
        if validate:
            xml_text = dom.toxml(encoding=charset)
        else:
            with DisabledValidation():
                xml_text = dom.toxml(encoding=charset)

        super().__init__(
            msg=xml_text, status=status, content_type='application/xml',
            charset=charset, encoding=None, cors=cors)


class JSON(Response):
    """A JSON response."""

    def __init__(self, dictionary, escape=True, strip=False, status=200,
                 cors=None, indent=None):
        """Initializes raiseable WSGI response with
        the given dictionary d as JSON response.
        """
        if strip:
            dictionary = strip_json(dictionary)

        if escape:
            dictionary = escape_object(dictionary)

        super().__init__(
            msg=json_dumps(dictionary, indent=indent), status=status,
            content_type='application/json', encoding=True, cors=cors)


class Binary(Response):
    """A binary reply."""

    def __init__(self, data, status=200, cors=None, etag=None, filename=None):
        """Initializes raiseable WSGI response
        with binary data and an optional etag.
        """
        super().__init__(
            msg=data, status=status, content_type=mimetype(data),
            charset=None, encoding=None, cors=cors)
        self._etag = None
        self._filename = None
        self.etag = etag
        self.filename = filename

    @property
    def etag(self):
        """Returns the e-tag."""
        return self._filename

    @etag.setter
    def etag(self, etag):
        """Sets the e-tag."""
        self._etag = etag

        if etag is not None:
            if etag is True:
                etag = sha256(self.response_body).hexdigest()

            self.headers.fields['ETag'] = etag

    @property
    def filename(self):
        """Returns the file name."""
        return self._filename

    @filename.setter
    def filename(self, filename):
        """Sets the file name.

        Setting the file name to None will also remove
        any Content-Disposition header field.
        """
        self._filename = filename

        if filename is not None:
            content_disposition = 'attachment; filename="{}"'.format(filename)
            self.headers.fields['Content-Disposition'] = content_disposition
        else:
            self.headers.fields.pop('Content-Disposition', None)


class InternalServerError(Error):
    """A code-500 WSGI response."""

    def __init__(self, msg=None, charset='utf-8', cors=True):
        """Indicates an internal server error
        CORS is enabled by default.
        """
        if msg is None:
            msg = 'Internal Server Error'

        super().__init__(msg=msg, status=500, charset=charset, cors=cors)


class PostData:
    """Represents POST-ed data."""

    file_too_large = Error('File too large.', status=507)
    no_data_provided = Error('No data provided.')
    non_utf8_data = Error('POST-ed data is not UTF-8 text.')
    non_json_data = Error('Text is not vaid JSON.')
    no_dom_specified = Error('No DOM specified.')
    invalid_xml_data = Error('Invalid data for XML DOM.')

    def __init__(self, wsgi_input, dom=None):
        """Sets the WSGI input and optional error handlers."""
        self.wsgi_input = wsgi_input
        self.dom = dom

    @property
    @lru_cache(maxsize=1)
    def bytes(self):
        """Reads and returns the POST-ed data."""
        if self.wsgi_input is None:
            raise self.no_data_provided from None

        try:
            return self.wsgi_input.read()
        except MemoryError:
            raise self.file_too_large from None

    @property
    @lru_cache(maxsize=1)
    def text(self):
        """Returns UTF-8 text."""
        try:
            return self.bytes.decode()
        except UnicodeDecodeError:
            raise self.non_utf8_data from None

    @property
    def json(self):
        """Returns a JSON-ish dictionary."""
        try:
            return json_loads(self.text)
        except ValueError:
            raise self.non_json_data from None

    @property
    def xml(self):
        """Loads XML data into the provided DOM model."""
        if self.dom is None:
            raise self.no_dom_specified

        try:
            return self.dom.CreateFromDocument(self.text)
        except PyXBException:
            raise self.invalid_xml_data from None


class RequestHandler(LoggingClass):
    """Request handling wrapper for WsgiApps."""

    DATA_HANDLER = PostData

    def __init__(self, environ, unquote=True, logger=None):
        """Sets the environ and additional configuration parameters."""
        super().__init__(logger=logger)
        self.environ = environ
        self.query = query_to_dict(self.query_string, unquote=unquote)
        self.data = self.DATA_HANDLER(environ.get('wsgi.input'))
        self.methods = {
            'GET': self.get,
            'POST': self.post,
            'PUT': self.put,
            'PATCH': self.patch,
            'DELETE': self.delete,
            'OPTIONS': self.options,
            'HEAD': self.head,
            'TRACE': self.trace,
            'PROPFIND': self.propfind,
            'COPY': self.copy,
            'MOVE': self.move}

    def __call__(self):
        """Call respective method and catch any exception."""
        try:
            return self.method()
        except KeyError:
            return Error('Invalid HTTP method: "{}"'.format(
                self.environ.get('REQUEST_METHOD')))
        except NotImplementedError:
            return Error('HTTP method "{}" is not implemented'.format(
                self.environ.get('REQUEST_METHOD')), status=501)

    @property
    @lru_cache(maxsize=1)
    def request_method(self):
        """Returns the request method."""
        return self.environ['REQUEST_METHOD']

    @property
    @lru_cache(maxsize=1)
    def path_info(self):
        """Returns the URL path."""
        return latin2utf(self.environ.get('PATH_INFO'))

    @property
    @lru_cache(maxsize=1)
    def query_string(self):
        """Returns the query string."""
        return self.environ.get('QUERY_STRING')

    @property
    @lru_cache(maxsize=1)
    def method(self):
        """Returns the method to invoke and its respective arguments."""
        return self.methods[self.request_method]

    @property
    @lru_cache(maxsize=1)
    def path(self):
        """Returns a list of elements of the path."""
        try:
            return [node for node in self.path_info.split('/') if node]
        except TypeError:
            return []

    def get(self):
        """Processes GET requests."""
        raise NotImplementedError()

    def post(self):
        """Processes POST requests."""
        raise NotImplementedError()

    def put(self):
        """Processes PUT requests."""
        raise NotImplementedError()

    def patch(self):
        """Processes PATCH requests."""
        raise NotImplementedError()

    def delete(self):
        """Processes DELETE requests."""
        raise NotImplementedError()

    def options(self):
        """Processes OPTIONS requests."""
        raise NotImplementedError()

    def head(self):
        """Processes HEAD requests."""
        raise NotImplementedError()

    def trace(self):
        """Processes TRACE requests."""
        raise NotImplementedError()

    def propfind(self):
        """Processes PROPFIND requests."""
        raise NotImplementedError()

    def copy(self):
        """Processes COPY requests."""
        raise NotImplementedError()

    def move(self):
        """Processes MOVE requests."""
        raise NotImplementedError()

    def logerr(self, message, status=400):
        """Logs the message as an error and raises it as a WSGI error"""
        self.logger.error(message)
        return Error(message, status=status)


class WsgiApp(LoggingClass):
    """Abstract WSGI application."""

    def __init__(self, request_handler, unquote=True, cors=None, debug=False):
        """Sets request handler, unquote and CORS flags and debug mode."""
        super().__init__(debug=debug)
        self.request_handler = request_handler
        self.unquote = unquote
        self.cors = cors
        self.debug = debug

    def __call__(self, environ, start_response):
        """Handles a WSGI query."""
        status, response_headers, response_body = self._run(environ)
        start_response(status, response_headers)

        if response_body is not None:
            yield response_body

    def _run(self, environ):
        """Instantiates and calls the request handler,
        handles errors and returns response.
        """
        try:
            response = self.request_handler(
                environ, unquote=self.unquote, logger=self.logger)()
        except Response as response:
            response.cors = self.cors
            return response
        except Exception:
            message = format_exc()
            self.logger.error(message)

            if self.debug:
                return InternalServerError(msg=message, cors=self.cors)

            return InternalServerError(cors=self.cors)

        response.cors = self.cors
        return response
