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
"""Response types."""

from hashlib import sha256

from flask import Response as Response_

from mimeutil import mimetype as get_mimetype
from xmldom import DisabledValidation

from wsgilib.json import strip_json, escape_object, json_dumps

__all__ = [
    'Response',
    'PlainText',
    'Error',
    'OK',
    'HTML',
    'XML',
    'JSON',
    'Binary',
    'InternalServerError']


class Response(Exception, Response_):
    """An WSGI error message."""

    def __init__(self, msg=None, status=200, mimetype='text/plain',
                 charset='utf-8', encoding=True, headers=None):
        """Generates an error WSGI response."""
        Exception.__init__(self, msg)
        msg = msg or ''

        if encoding:
            msg = msg.encode(encoding=charset)

        if charset is not None:
            content_type = '{}; charset={}'.format(mimetype, charset)
            Response_.__init__(
                self, response=msg, status=status, headers=headers,
                content_type=content_type)
        else:
            Response_.__init__(
                self, response=msg, status=status, headers=headers,
                mimetype=mimetype)


class PlainText(Response):
    """Returns a successful plain text response."""

    def __init__(self, msg=None, status=200, charset='utf-8'):
        """Returns a plain text success response."""
        super().__init__(
            msg=msg, status=status, mimetype='text/plain',
            charset=charset, encoding=True)


class Error(PlainText):
    """An WSGI error message."""

    def __init__(self, msg=None, status=400, charset='utf-8'):
        """Returns a plain text error response."""
        if 400 <= status < 600:
            super().__init__(msg, status=status, charset=charset)
        else:
            raise ValueError('Not an error status: {}'.format(status))


class OK(PlainText):
    """Returns a successful plain text response."""

    def __init__(self, msg=None, status=200, charset='utf-8'):
        """Returns a plain text success response."""
        if 200 <= status < 300:
            super().__init__(msg=msg, status=status, charset=charset)
        else:
            raise ValueError('Not a success status: {}'.format(status))


class HTML(Response):
    """Returns a successful plain text response."""

    def __init__(self, msg=None, status=200, charset='utf-8'):
        """Returns a plain text success response."""
        super().__init__(
            msg=msg, status=status, mimetype='text/html',
            charset=charset, encoding=True)


class XML(Response):
    """An XML response."""

    def __init__(self, dom, validate=True, status=200, charset='utf-8'):
        """Sets the dom and inherited responde attributes."""
        if validate:
            xml_text = dom.toxml(encoding=charset)
        else:
            with DisabledValidation():
                xml_text = dom.toxml(encoding=charset)

        super().__init__(
            msg=xml_text, status=status, mimetype='application/xml',
            charset=charset, encoding=None)


class JSON(Response):
    """A JSON response."""

    def __init__(self, dictionary, strip=False, status=200, indent=None):
        """Initializes raiseable WSGI response with
        the given dictionary d as JSON response.
        """
        if strip:
            dictionary = strip_json(dictionary)

        super().__init__(
            msg=json_dumps(escape_object(dictionary), indent=indent),
            status=status, mimetype='application/json', encoding=True)


class Binary(Response):
    """A binary reply."""

    def __init__(self, data, status=200, etag=None, filename=None):
        """Initializes raiseable WSGI response
        with binary data and an optional etag.
        """
        super().__init__(
            msg=data, status=status, mimetype=get_mimetype(data),
            charset=None, encoding=False)
        self._filename = None
        self.etag = etag
        self.filename = filename

    @property
    def response_checksum(self):
        """Returns the SHA-256 checksum of the response."""
        if self.response:
            sha256sum = sha256()

            for response in self.response:
                sha256sum.update(response)

            return sha256sum.hexdigest()

        raise ValueError('No response available to hash.')

    @property
    def etag(self):
        """Returns the e-tag."""
        return self.headers.get('ETag')

    @etag.setter
    def etag(self, etag):
        """Sets the e-tag."""
        if etag is None:
            self.headers.pop('ETag', None)
        else:
            if etag is True:
                etag = self.response_checksum

            self.headers['ETag'] = etag

    @property
    def filename(self):
        """Yields all file names."""
        try:
            content_disposition = self.headers['Content-Disposition']
        except KeyError:
            return None

        _, filename = content_disposition.split('; ')
        _, filename, _ = filename.split('"')
        return filename

    @filename.setter
    def filename(self, filename):
        """Sets the file name.

        Setting the file name to None will also remove
        any Content-Disposition header field.
        """
        if filename is None:
            self.headers.pop('Content-Disposition', None)
        else:
            content_disposition = 'attachment; filename="{}"'.format(filename)
            self.headers['Content-Disposition'] = content_disposition

    @filename.deleter
    def filename(self):
        """Deletes all file names."""
        self.headers = [
            (key, value) for key, value in self.headers
            if key != 'Content-Disposition']


class InternalServerError(Response):
    """A code-500 WSGI response."""

    def __init__(self, msg='Internal Server Error.', charset='utf-8'):
        """Indicates an internal server error
        CORS is enabled by default.
        """
        super().__init__(msg=msg, status=500, charset=charset)
