#  wsgilib
#  Copyright (C) 2017  HOMEINFO - Digitale Informationssysteme GmbH
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
"""Simple (U)WSGI framework for web applications"""

from hashlib import sha256
from html import escape
from json import dumps
from traceback import format_exc
from urllib import parse

from fancylog import LoggingClass
from mimeutil import mimetype
from strflib import latin2utf
from xmldom import DisabledValidation

__all__ = [
    'escape_object',
    'strip_json',
    'HTTP_STATUS',
    'query2dict',
    'cors',
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
    'RequestHandler',
    'WsgiApp',
    'ResourceHandler',
    'RestApp']


def escape_object(obj):
    """Escapes HTML code withtin the provided object"""

    if isinstance(obj, str):
        return escape(obj)
    elif isinstance(obj, list):
        return [escape_object(item) for item in obj]
    elif isinstance(obj, dict):
        for key in obj:
            obj[key] = escape_object(obj[key])

    return obj


def strip_json(dict_or_list):
    """Strips empty data from JSON-like objects"""

    if isinstance(dict_or_list, dict):
        result = {}

        for key in dict_or_list:
            value = dict_or_list[key]

            if isinstance(value, (dict, list)):
                stripped = strip_json(value)

                if stripped:
                    result[key] = stripped
            elif value is None:
                continue
            else:
                result[key] = value
    elif isinstance(dict_or_list, list):
        result = []

        for element in dict_or_list:
            if isinstance(element, (dict, list)):
                stripped = strip_json(element)

                if stripped:
                    result.append(stripped)
            else:
                result.append(element)
    else:
        raise ValueError('Object must be dict or list.')

    return result


def is_handler(obj):
    """Checks if the respective object implements ResourceHandler"""

    try:
        return issubclass(obj, ResourceHandler)
    except TypeError:
        return False


def get_handler_and_resource(handler, revpath, pathsep='/'):
    """Splits the path into the respective handler and resource"""

    handled_path = []

    while revpath:
        node = revpath.pop()
        handled_path.append(node)

        try:
            handler = handler[node]
        except (KeyError, TypeError):
            revpath.append(node)
            break

    if revpath:
        resource = pathsep.join(reversed(revpath))
    else:
        resource = None

    if is_handler(handler):
        return (handler, resource)
    else:
        raise Error('Not a ReST handler: {}.'.format(
            pathsep.join(handled_path)), status=400)


# A dictionary of valid HTTP status codes
HTTP_STATUS = {
    100: 'Continue',
    101: 'Switching Protocols',
    102: 'Processing',
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi-Status',
    208: 'Already Reported',
    226: 'IM Used',
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    306: 'Switch Proxy',  # Deprecated!
    307: 'Temporary Redirect',
    308: 'Permanent Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Time-out',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request-URL Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested range not satisfiable',
    417: 'Expectation Failed',
    420: 'Policy Not Fulfilled',
    421: 'Misdirected Request',
    422: 'Unprocessable Entity',
    423: 'Locked',
    424: 'Failed Dependency',
    426: 'Upgrade Required',
    428: 'Precondition Required',
    429: 'Too Many Requests',
    431: 'Request Header Fields Too Large',
    451: 'Unavailable For Legal Reasons',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Time-out',
    505: 'HTTP Version not supported',
    506: 'Variant Also Negotiates',
    507: 'Insufficient Storage',
    508: 'Loop Detected',
    509: 'Bandwidth Limit Exceeded',
    510: 'Not Extended',
    511: 'Network Authentication Required'}


def query2dict(query, unquote=True):
    """Converts a query string into a dictionary"""

    result = {}

    if query:
        for param_data in query.split('&'):
            # Skip empty parameter data
            if param_data:
                fragments = param_data.split('=')
                param = fragments[0]

                # Skip empty-named parameters
                if param:
                    if len(fragments) == 1:
                        value = True
                    else:
                        value = '='.join(fragments[1:])

                        if unquote:
                            value = parse.unquote(value)

                    result[param] = value

    return result


def cors(response, cors):
    """Fixes CORS settings on the respective response"""

    if response.headers.cors is None:
        response.headers.cors = cors

    return response


class Headers():
    """Wraps response headers"""

    def __init__(self, content_type=None, content_length=None,
                 charset=None, cors=None, fields=None):
        """ Generates response headers"""
        self.content_type = content_type
        self.content_length = content_length
        self.charset = charset
        self.cors = cors
        self.fields = fields or {}

    def __iter__(self):
        """Yields items"""
        if self.content_type is not None:
            if self.charset is not None:
                charset = 'charset={}'.format(self.charset)
                content_type = '{};{}'.format(self.content_type, charset)
            else:
                content_type = self.content_type

            yield ('Content-Type', content_type)

        if self.content_length is not None:
            yield ('Content-Length', str(self.content_length))

        # Cross-origin resource sharing
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

        # Optional fields
        for field in self.fields:
            yield (field, self.fields[field])


class WsgiResponse():
    """A WSGI response"""

    def __init__(self, status, content_type=None, response_body=None,
                 charset=None, cors=None, fields=None):
        """Creates a generic WSGI response"""
        self.status = (status, HTTP_STATUS[status])

        try:
            content_length = len(response_body)
        except TypeError:
            content_length = None

        self.headers = Headers(
            content_type, content_length, charset=charset, cors=cors,
            fields=fields)
        self.response_body = response_body

    def __iter__(self):
        """Yields properties"""
        yield '{} {}'.format(self.status)
        # Headers must be a list at this point
        yield list(self.headers)
        yield self.response_body


class Response(Exception, WsgiResponse):
    """An WSGI error message"""

    def __init__(self, msg=None, status=200, content_type='text/plain',
                 charset='utf-8', encoding=True, cors=None):
        """Generates an error WSGI response"""
        if msg is not None:
            if encoding is True:
                encoding = charset

            if encoding:
                msg = msg.encode(encoding=charset)

        Exception.__init__(self, msg)
        WsgiResponse.__init__(
            self, status, content_type=content_type, response_body=msg,
            charset=charset, cors=cors)


class PlainText(Response):
    """Returns a successful plain text response"""

    def __init__(self, msg=None, status=200, charset='utf-8', cors=None):
        """Returns a plain text success response"""
        super().__init__(
            msg=msg, status=status, content_type='text/plain',
            charset=charset, encoding=True, cors=cors)


class Error(PlainText):
    """An WSGI error message"""

    def __init__(self, msg=None, status=400, charset='utf-8', cors=None):
        """Returns a plain text error response"""
        if 400 <= status < 600:
            super().__init__(
                msg=msg, status=status, charset=charset, cors=cors)
        else:
            raise ValueError('Not an error status: {}'.format(status))


class OK(PlainText):
    """Returns a successful plain text response"""

    def __init__(self, msg=None, status=200, charset='utf-8', cors=None):
        """Returns a plain text success response"""
        if 200 <= status < 300:
            super().__init__(
                msg=msg, status=status, charset=charset, cors=cors)
        else:
            raise ValueError('Not a success status: {}'.format(status))


class HTML(Response):
    """Returns a successful plain text response"""

    def __init__(self, msg=None, status=200, charset='utf-8', cors=None):
        """Returns a plain text success response"""
        super().__init__(
            msg=msg, status=status, content_type='text/html',
            charset=charset, encoding=True, cors=cors)


class XML(Response):
    """An XML response"""

    def __init__(self, dom, validate=True, status=200, charset='utf-8',
                 cors=None):
        if validate:
            xml_text = dom.toxml(encoding=charset)
        else:
            with DisabledValidation():
                xml_text = dom.toxml(encoding=charset)

        super().__init__(
            msg=xml_text, status=status, content_type='application/xml',
            charset=charset, encoding=None, cors=cors)


class JSON(Response):
    """A JSON response"""

    def __init__(self, d, strip=True, escape=True, status=200, cors=None,
                 indent=None):
        """Initializes raiseable WSGI response with
        the given dictionary d as JSON response
        """
        if strip:
            d = strip_json(d)

        if escape:
            d = escape_object(d)

        super().__init__(
            msg=dumps(d, indent=indent), status=status,
            content_type='application/json', encoding=True, cors=cors)


class Binary(Response):
    """A binary reply"""

    def __init__(self, data, status=200, cors=None, etag=None):
        """Initializes raiseable WSGI response
        with binary data and an optional etag
        """
        super().__init__(
            msg=data, status=status, content_type=mimetype(data),
            charset=None, encoding=None, cors=cors)

        if etag is True:
            etag = sha256(data).hexdigest()

        if etag:
            self.headers.fields['ETag'] = etag


class InternalServerError(Error):
    """A code-500 WSGI response"""

    def __init__(self, msg=None, charset='utf-8', cors=True):
        """Indicates an internal server error
        CORS is enabled by default
        """
        if msg is None:
            msg = 'Internal Server Error'

        super().__init__(msg=msg, status=500, charset=charset, cors=cors)


class RequestHandler(LoggingClass):
    """Request handling wrapper for WsgiApps"""

    def __init__(self, environ, unquote=True, logger=None, testable=False):
        super().__init__(logger=logger)
        self.environ = environ
        self.query = query2dict(self.query_string, unquote=unquote)
        self._data_cache = False
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

        if testable:
            self.methods['PROBE'] = self.__probe

    def __call__(self):
        """Call respective method and catch any exception

        TODO: Put methods in a dictionary
        """
        try:
            return self.method()
        except KeyError:
            return Error('Invalid HTTP method: "{}"'.format(
                self.environ.get('REQUEST_METHOD')))
        except NotImplementedError:
            return Error('HTTP method "{}" is not implemented'.format(
                self.environ.get('REQUEST_METHOD')), status=501)

    @property
    def data(self):
        """Returns the data sent over HTTP"""
        if self._data_cache is False:
            try:
                self._data_cache = self.environ['wsgi.input'].read()
            except KeyError:
                self._data_cache = None
            except MemoryError:
                self._data_cache = None
                raise Error('File too large.', status=507) from None

        return self._data_cache

    @property
    def request_method(self):
        """Returns the request method"""
        return self.environ['REQUEST_METHOD']

    @property
    def path_info(self):
        """Returns the URL path"""
        return latin2utf(self.environ.get('PATH_INFO'))

    @property
    def query_string(self):
        """Returns the query string"""
        return self.environ.get('QUERY_STRING')

    @property
    def method(self):
        """Returns the method to invoke and its respective arguments"""
        return self.methods[self.request_method]

    @property
    def path(self):
        """Returns a list of elements of the path"""
        try:
            return [node for node in self.path_info.split('/') if node]
        except TypeError:
            return []

    def get(self):
        raise NotImplementedError()

    def post(self, data):
        raise NotImplementedError()

    def put(self, data):
        raise NotImplementedError()

    def patch(self, data):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    def options(self):
        raise NotImplementedError()

    def head(self):
        raise NotImplementedError()

    def trace(self):
        raise NotImplementedError()

    def propfind(self):
        raise NotImplementedError()

    def copy(self):
        raise NotImplementedError()

    def move(self):
        raise NotImplementedError()

    def __probe(self):
        """Tests whether the WSGI app is running"""
        return OK('running')

    def logerr(self, message, status=400):
        """Logs the message as an error and raises it as a WSGI error"""
        self.logger.error(message)
        return Error(message, status=status)


class WsgiApp(LoggingClass):
    """Abstract WSGI application"""

    def __init__(self, request_handler, unquote=True, cors=None, logger=None,
                 debug=False, log_level=None, testable=False):
        """Sets CORS flags and logger"""
        super().__init__(logger=logger, debug=debug, level=log_level)
        self.request_handler = request_handler
        self.unquote = unquote
        self.cors = cors
        self.testable = testable

    def __call__(self, environ, start_response):
        """Handles a WSGI query"""
        status, response_headers, response_body = self._run(environ)
        start_response(status, response_headers)

        if response_body is not None:
            yield response_body

    def _run(self, environ):
        """Returns the approriate WSGI response"""
        try:
            request_handler = self.request_handler(
                environ, unquote=self.unquote, logger=self.logger,
                testable=self.testable)
            return cors(request_handler(), self.cors)
        except Response as response:
            return cors(response, self.cors)
        except Exception:
            if self.debug:
                msg = format_exc()
                self.logger.error(msg)
                return InternalServerError(msg=msg, cors=self.cors)
            else:
                return InternalServerError(cors=self.cors)


class ResourceHandler(RequestHandler):
    """Handles a certain resource"""

    HANDLERS = None

    def __init__(self, resource, environ, unquote=True, logger=None,
                 testable=False):
        """Invokes the super constructor and sets resource"""
        super().__init__(
            environ, unquote=unquote, logger=logger, testable=testable)
        self.resource = resource


class RestApp(WsgiApp):
    """A RESTful web application"""

    PATHSEP = '/'

    def __init__(self, handlers, unquote=True, cors=None, logger=None,
                 debug=False, log_level=None, testable=False):
        """Sets the root path for this web application"""
        super().__init__(
            self.resource_handler, unquote=unquote, cors=cors, logger=logger,
            debug=debug, log_level=log_level, testable=testable)
        self.handlers = handlers

    def resource_handler(self, environ, unquote=True, logger=None,
                         testable=False):
        """Returns the appropriate resource handler"""
        try:
            path = latin2utf(environ['PATH_INFO'])
        except KeyError:
            revpath = []
        else:
            revpath = [i for i in reversed(path.split(self.PATHSEP)) if i]

        handler, resource = get_handler_and_resource(
            self.handlers, revpath, pathsep=self.PATHSEP)
        return handler(resource, environ, unquote=unquote, logger=logger,
                       testable=testable)
