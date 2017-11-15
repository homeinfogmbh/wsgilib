"""Miscellaneous constants and functions."""

from collections import namedtuple
from contextlib import suppress
from datetime import datetime, date, time
from html import escape as escape_html
from json import dumps, loads
from urllib import parse

from strflib import latin2utf
from timelib import strpdatetime, strpdate, strptime


__all__ = [
    'DATE_TIME_TYPES',
    'PATH_SEP',
    'HTTP_STATUS',
    'RoutePlaceholder',
    'escape_object',
    'json_encode',
    'json_decode',
    'json_dumps',
    'json_loads',
    'strip_json',
    'query_items',
    'query_to_dict',
    'pathinfo',
    'iterpath']


DATE_TIME_TYPES = (datetime, date, time)
PATH_SEP = '/'
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
PLACEHOLDER_TYPES = {
    'str': str,
    'int': int,
    'bool': bool,
    'float': float}

RoutePlaceholder = namedtuple('RoutePlaceholder', ('name', 'value'))


def escape_object(obj):
    """Escapes HTML code withtin the provided object."""

    if isinstance(obj, str):
        return escape_html(obj)
    elif isinstance(obj, list):
        return [escape_object(item) for item in obj]
    elif isinstance(obj, dict):
        for key in obj:
            obj[key] = escape_object(obj[key])

    return obj


def json_encode(obj):
    """Encodes the object into a JSON-ish value."""

    if isinstance(obj, DATE_TIME_TYPES):
        return obj.isoformat()

    return obj


def json_decode(dictionary):
    """Decodes the JSON-ish dictionary values."""

    for key, value in dictionary.items():
        with suppress(TypeError, ValueError):
            dictionary[key] = strpdatetime(value)
            continue

        with suppress(TypeError, ValueError):
            dictionary[key] = strpdate(value)
            continue

        with suppress(TypeError, ValueError):
            dictionary[key] = strptime(value)
            continue

    return dictionary


def json_dumps(obj, *, default=json_encode, **kwargs):
    """Overrides json.dumps."""

    return dumps(obj, default=default, **kwargs)


def json_loads(string, *, object_hook=json_decode, **kwargs):
    """Overrides json.loads."""

    return loads(string, object_hook=object_hook, **kwargs)


def strip_json(dict_or_list):
    """Strips empty data from JSON-ish objects."""

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


def query_items(query_string, unquote=True, parsep='&', valsep='='):
    """Yields key-value pairs of the query string."""

    for parameter in query_string.split(parsep):
        # Skip empty parameter data.
        if parameter:
            fragments = parameter.split(valsep)
            key = fragments[0]

            # Skip empty-named parameters.
            if key:
                if len(fragments) == 1:
                    value = True
                else:
                    value = valsep.join(fragments[1:])

                    if unquote:
                        value = parse.unquote(value)

                yield (key, value)


def query_to_dict(query_string, unquote=True):
    """Converts a query string into a dictionary."""

    if query_string:
        return dict(query_items(query_string), unquote=unquote)

    return {}


def pathinfo(environ):
    """Extracts PATH_INFO from env dict."""

    path_info = environ.get('PATH_INFO')

    if path_info is not None:
        return latin2utf(path_info)

    return None


def iterpath(path):
    """Splits the path."""

    if path:
        for item in path.split(PATH_SEP):
            if item:
                yield item
