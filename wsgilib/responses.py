"""Response types."""

from hashlib import sha256
from re import compile  # pylint: disable=W0622
from xml.etree.ElementTree import tostring

from flask import Response as Response_

from mimeutil import mimetype as get_mimetype

from wsgilib.json import htmlescape, jsonify
from wsgilib.types import ETag, Message


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


CONTENT_DISPOSITION = compile('(\\w+)(?:; filename="(.+)")?')


class Response(Exception, Response_):   # pylint: disable=R0901
    """A raisable WSGI response."""

    def __init__(self, msg: Message = '', status: int = 200,
                 mimetype: str = 'text/plain', charset: str = 'utf-8',
                 encoding: bool = None, headers: dict = None):
        """Initializes Exception and Response superclasses."""
        Exception.__init__(self, msg)
        self.exceptions = None

        if encoding or encoding is None and isinstance(msg, str):
            msg = msg.encode(encoding=charset)

        if charset is None:
            Response_.__init__(
                self, response=msg, status=status, headers=headers,
                mimetype=mimetype)
        else:
            Response_.__init__(
                self, response=msg, status=status, headers=headers,
                content_type=f'{mimetype}; charset={charset}')

    def __enter__(self):
        """Returns itself."""
        if not self.exceptions:
            raise TypeError('Handling context without exceptions to convert.')

        return self

    def __exit__(self, typ, value, traceback):
        """Handles the respective exceptions."""
        self.exceptions, exceptions = None, self.exceptions

        if exceptions and isinstance(value, exceptions):
            raise self

    def convert(self, *exceptions):
        """Prepares the response to convert the specified
        exceptions to itself when exiting a context.
        """
        self.exceptions = exceptions
        return self


class PlainText(Response):  # pylint: disable=R0901
    """Returns a successful plain text response."""

    def __init__(self, msg: Message = '', status: int = 200,
                 charset: str = 'utf-8', headers: dict = None):
        """Returns a plain text success response."""
        super().__init__(
            msg=msg, status=status, mimetype='text/plain',
            charset=charset, encoding=True, headers=headers)


class Error(PlainText):     # pylint: disable=R0901
    """An WSGI error message."""

    def __init__(self, msg: Message = '', status: int = 400,
                 charset: str = 'utf-8', headers: dict = None):
        """Returns a plain text error response."""
        if 400 <= status < 600:
            super().__init__(
                msg, status=status, charset=charset, headers=headers)
        else:
            raise ValueError(f'Not an error status: {status}')


class OK(PlainText):    # pylint: disable=R0901
    """Returns a successful plain text response."""

    def __init__(self, msg: Message = '', status: int = 200,
                 charset: str = 'utf-8', headers: dict = None):
        """Returns a plain text success response."""
        if 200 <= status < 300:
            super().__init__(
                msg=msg, status=status, charset=charset, headers=headers)
        else:
            raise ValueError(f'Not a success status: {status}')


class HTML(Response):   # pylint: disable=R0901
    """Returns a successful plain text response."""

    def __init__(self, msg: object = '', status: int = 200,
                 charset: str = 'utf-8', headers: dict = None):
        """Returns a plain text success response."""
        try:
            msg = tostring(msg, encoding=charset, method='html')
        except AttributeError:
            encoding = None
        else:
            encoding = False

        super().__init__(
            msg=msg, status=status, mimetype='text/html', charset=charset,
            encoding=encoding, headers=headers)


class XML(Response):    # pylint: disable=R0901
    """An XML response."""

    def __init__(self, msg: object, status: int = 200, charset: str = 'utf-8',
                 headers: dict = None):
        """Sets the dom and inherited responde attributes."""
        try:
            msg = msg.toxml(encoding=charset)
        except AttributeError:
            try:
                msg = tostring(msg, encoding=charset, method='xml')
            except AttributeError:
                encoding = None
            else:
                encoding = False
        else:
            encoding = False

        super().__init__(
            msg=msg, status=status, mimetype='application/xml',
            charset=charset, encoding=encoding, headers=headers)


class JSON(Response):   # pylint: disable=R0901
    """A JSON response."""

    def __init__(self, json: object, status: int = 200, indent: int = None,
                 headers: dict = None):
        """Initializes raiseable WSGI response with
        the given dictionary d as JSON response.
        """
        super().__init__(
            msg=jsonify(htmlescape(json), indent=indent),
            status=status, mimetype='application/json', encoding=True,
            headers=headers)


class Binary(Response):     # pylint: disable=R0901
    """A binary reply."""

    def __init__(self, msg: bytes, status: int = 200, etag: ETag = None,
                 filename: str = None, headers: dict = None):
        """Initializes raiseable WSGI response
        with binary data and an optional etag.
        """
        super().__init__(
            msg=msg, status=status, mimetype=get_mimetype(msg),
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

        match = CONTENT_DISPOSITION.fullmatch(content_disposition)

        if match is None:
            return None

        _, filename = match.groups()
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


class InternalServerError(Error):   # pylint: disable=R0901
    """A code-500 WSGI response."""

    def __init__(self, msg: Message = 'Internal Server Error.',
                 charset: str = 'utf-8', headers: dict = None):
        """Indicates an internal server error."""
        super().__init__(msg=msg, status=500, charset=charset, headers=headers)
