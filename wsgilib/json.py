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
"""Miscellaneous constants and functions."""

from contextlib import suppress
from datetime import datetime, date, time
from html import escape as escape_html
from json import dumps, loads

from timelib import strpdatetime, strpdate, strptime


__all__ = [
    'DATE_TIME_TYPES',
    'escape_object',
    'json_encode',
    'json_decode',
    'json_dumps',
    'json_loads',
    'strip_json']


DATE_TIME_TYPES = (datetime, date, time)


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
