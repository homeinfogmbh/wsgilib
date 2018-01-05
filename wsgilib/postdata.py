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
"""Post data handling."""

from functools import lru_cache
from logging import basicConfig, getLogger

from flask import request

try:
    from pyxb import PyXBException
except ImportError:
    basicConfig()
    getLogger().warning('PyXB not installed. XML error handling unavailable.')

from wsgilib.json import json_loads
from wsgilib.responses import Error

__all__ = ['PostData']


@lru_cache(maxsize=1)
def bytes_to_text(bytes_):
    """Converts bytes to text."""

    return bytes_.decode()


@lru_cache(maxsize=1)
def text_to_json(text):
    """Converts text into a JSON object."""

    return json_loads(text)


@lru_cache(maxsize=1)
def text_to_dom(dom, text):
    """Converts text into a JSON object."""

    return dom.CreateFromDocument(text)


class PostData:
    """Represents POST-ed data."""

    def __init__(self, **errors):
        """Sets the WSGI input and optional error handlers."""
        self.file_too_large = errors.get(
            'file_too_large', Error('File too large.', status=507))
        self.no_data_provided = errors.get(
            'no_data_provided', Error('No data provided.'))
        self.non_utf8_data = errors.get(
            'non_utf8_data', Error('POST-ed data is not UTF-8 text.'))
        self.non_json_data = errors.get(
            'non_json_data', Error('Text is not valid JSON.'))
        self.invalid_xml_data = errors.get(
            'invalid_xml_data', Error('Invalid data for XML DOM.'))

    @property
    def bytes(self):
        """Reads and returns the POST-ed data."""
        try:
            return request.get_data()
        except MemoryError:
            raise self.file_too_large

    @property
    def text(self):
        """Returns UTF-8 text."""
        try:
            return bytes_to_text(self.bytes)
        except UnicodeDecodeError:
            raise self.non_utf8_data

    @property
    def json(self):
        """Returns a JSON-ish dictionary."""
        try:
            return text_to_json(self.text)
        except ValueError:
            raise self.non_json_data

    def xml(self, dom):
        """Loads XML data into the provided DOM model."""
        try:
            return text_to_dom(dom, self.text)
        except PyXBException:
            raise self.invalid_xml_data
