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

from functools import partial
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


class _BytesParser:
    """File that has several parsing properties."""

    def __init__(self, *, file_too_large=None, no_data_provided=None,
                 non_utf8_data=None, non_json_data=None,
                 invalid_xml_data=None):
        """Sets the WSGI input and optional error handlers."""
        self.file_too_large = file_too_large or partial(
            Error, 'File too large.', status=507)
        self.no_data_provided = no_data_provided or partial(
            Error, 'No data provided.')
        self.non_utf8_data = non_utf8_data or partial(
            Error, 'POST-ed data is not UTF-8 text.')
        self.non_json_data = non_json_data or partial(
            Error, 'Text is not valid JSON.')
        self.invalid_xml_data = invalid_xml_data or partial(
            Error, 'Invalid data for XML DOM.')

    @property
    def bytes(self):
        """Returns bytes."""
        raise NotImplementedError()

    @property
    def text(self):
        """Returns UTF-8 text."""
        try:
            return self.bytes.decode()
        except UnicodeDecodeError:
            raise self.non_utf8_data()

    @property
    def json(self):
        """Returns a JSON-ish value."""
        try:
            return json_loads(self.text)
        except ValueError:
            raise self.non_json_data()

    def xml(self, dom):
        """Loads XML data into the provided DOM model."""
        try:
            return dom.CreateFromDocument(self.text)
        except PyXBException:
            raise self.invalid_xml_data()


class PostData(_BytesParser):
    """Represents POST-ed data."""

    def __iter__(self):
        """Yields the respective files, iff any."""
        return self.files

    def __bytes__(self):
        """Returns the respective bytes."""
        return self.bytes

    @property
    def files(self):
        """Yields the respective files, iff any."""
        return {
            name: _PostFile(
                file_storage, file_too_large=self.file_too_large,
                no_data_provided=self.no_data_provided,
                non_utf8_data=self.non_utf8_data,
                non_json_data=self.non_json_data,
                invalid_xml_data=self.invalid_xml_data)
            for name, file_storage in request.files.items()}

    @property
    def bytes(self):
        """Reads and returns the POST-ed data."""
        try:
            return request.get_data()
        except MemoryError:
            raise self.file_too_large()


class _PostFile(_BytesParser):
    """Represents a POSTed file."""

    def __init__(self, file_storage, **errors):
        """Sets name and file."""
        super().__init__(**errors)
        self.file_storage = file_storage

    def __bytes__(self):
        """Returns the respective bytes."""
        return self.bytes

    @property
    def bytes(self):
        """Returns the respective bytes."""
        try:
            return self.file_storage.stream.read()
        except MemoryError:
            raise self.file_too_large()
