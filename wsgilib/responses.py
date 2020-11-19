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

from contextlib import suppress
from hashlib import sha256
from xml.etree.ElementTree import tostring

from flask import Response as Response_

from mimeutil import mimetype as get_mimetype

from wsgilib.json import escape_object, json_dumps


__all__ = [
    'Response',
    'PlainText',
    'Error',
    'OK',
    'HTML',
    'XML',
    'JSON',
    'Binary',
    'InternalServerError'
]


class Response(Exception, Response_):   # pylint: disable=R0901
    """A raisable WSGI response."""

    def __init__(self, msg=None, status=200, mimetype='text/plain',
                 charset='utf-8', encoding=True, headers=None):
        """Initializes Exception and Response superclasses."""
        Exception.__init__(self, msg)
        self._exceptions = ()
        msg = msg or ''

        if encoding:
            msg = msg.encode(encoding=charset)

        if charset is not None:
            content_type = f'{mimetype}; charset={charset}'
            Response_.__init__(
                self, response=msg, status=status, headers=headers,
                content_type=content_type)
        else:
            Response_.__init__(
                self, response=msg, status=status, headers=headers,
                mimetype=mimetype)

    def __enter__(self):
        """Returns itself."""
        if not self._exceptions:
            raise TypeError('Handling context without exceptions to convert.')

        return self

    def __exit__(self, typ, value, traceback):
        """Handles the respective exceptions."""
        self._exceptions, exceptions = (), self._exceptions

        if exceptions and isinstance(value, exceptions):
            raise self

    def convert(self, *exceptions):
        """Prepares the response to convert the specified
        exceptions to itself when exiting a context.
        """
        self._exceptions = exceptions
        return self


class PlainText(Response):  # pylint: disable=R0901
    """Returns a successful plain text response."""

    def __init__(self, msg=None, status=200, charset='utf-8', headers=None):
        """Returns a plain text success response."""
        super().__init__(
            msg=msg, status=status, mimetype='text/plain',
            charset=charset, encoding=True, headers=headers)


class Error(PlainText):     # pylint: disable=R0901
    """An WSGI error message."""

    def __init__(self, msg=None, status=400, charset='utf-8', headers=None):
        """Returns a plain text error response."""
        if 400 <= status < 600:
            super().__init__(
                msg, status=status, charset=charset, headers=headers)
        else:
            raise ValueError(f'Not an error status: {status}')


class OK(PlainText):    # pylint: disable=R0901
    """Returns a successful plain text response."""

    def __init__(self, msg=None, status=200, charset='utf-8', headers=None):
        """Returns a plain text success response."""
        if 200 <= status < 300:
            super().__init__(
                msg=msg, status=status, charset=charset, headers=headers)
        else:
            raise ValueError(f'Not a success status: {status}')


class HTML(Response):   # pylint: disable=R0901
    """Returns a successful plain text response."""

    def __init__(self, msg=None, status=200, charset='utf-8', headers=None):
        """Returns a plain text success response."""
        with suppress(AttributeError):
            msg = tostring(msg)

        super().__init__(
            msg=msg, status=status, mimetype='text/html',
            charset=charset, encoding=True, headers=headers)


class XML(Response):    # pylint: disable=R0901
    """An XML response."""

    def __init__(self, dom, status=200, charset='utf-8', headers=None):
        """Sets the dom and inherited responde attributes."""
        super().__init__(
            msg=dom.toxml(encoding=charset), status=status,
            mimetype='application/xml', charset=charset, encoding=None,
            headers=headers)


class JSON(Response):   # pylint: disable=R0901
    """A JSON response."""

    def __init__(self, json, status=200, indent=None, headers=None):
        """Initializes raiseable WSGI response with
        the given dictionary d as JSON response.
        """
        super().__init__(
            msg=json_dumps(escape_object(json), indent=indent),
            status=status, mimetype='application/json', encoding=True,
            headers=headers)


class Binary(Response):     # pylint: disable=R0901
    """A binary reply."""

    def __init__(self, data, status=200, etag=None, filename=None,
                 headers=None):
        """Initializes raiseable WSGI response
        with binary data and an optional etag.
        """
        super().__init__(
            msg=data, status=status, mimetype=get_mimetype(data),
            charset=None, encoding=False, headers=headers)
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
        """Sets the e-tag.
        If etag is None, the etag will default
        to the content's SHA-256 checksum.
        """
        if etag is None:
            return

        if etag is True:
            self.headers['ETag'] = self.response_checksum
        elif etag is False:
            self.headers.pop('ETag', None)
        else:
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
            content_disposition = f'attachment; filename="{filename}"'
            self.headers['Content-Disposition'] = content_disposition


class InternalServerError(Response):    # pylint: disable=R0901
    """A code-500 WSGI response."""

    def __init__(self, msg='Internal Server Error.', charset='utf-8',
                 headers=None):
        """Indicates an internal server error."""
        super().__init__(msg=msg, status=500, charset=charset, headers=headers)
