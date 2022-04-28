"""Response types."""

from __future__ import annotations
from hashlib import sha256
from re import fullmatch
from typing import Any, Callable, Optional, Union
from xml.etree.ElementTree import tostring

from flask import Response as Response_
from werkzeug.datastructures import Headers

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


CD_REGEX = '(\\w+)(?:; filename="(.+)")?'


class Response(Exception):
    """A WSGI response that can be raised as an exception."""

    def __init__(
            self,
            msg: Message = '',
            status: int = 200,
            *,
            mimetype: str = 'text/plain',
            charset: Optional[str] = 'utf-8',
            encoding: bool = None,
            headers: dict = None
    ):
        super().__init__()
        self.msg = msg
        self.status = status
        self.mimetype = mimetype
        self.charset = charset
        self.encoding = encoding
        self.headers = Headers(headers)
        self._exceptions = None

    def __call__(self, environ: dict, start_response: Callable):
        """Implements the flask.Response interface."""
        return self.response(environ, start_response)

    def __enter__(self):
        """Returns itself."""
        if not self._exceptions:
            raise TypeError('Handling context without exceptions to convert.')

        return self

    def __exit__(self, typ, value, traceback):
        """Handles the respective exceptions."""
        self._exceptions, exceptions = None, self._exceptions

        if exceptions and isinstance(value, exceptions):
            raise self

    @property
    def body(self) -> bytes:
        """Returns the body as bytes."""
        if self.encoding:
            return self.msg.encode(encoding=self.charset)

        if self.encoding is None and isinstance(self.msg, str):
            return self.msg.encode(encoding=self.charset)

        return self.msg

    @property
    def response(self) -> Response_:
        """Returns an appropriate response object."""
        if self.charset is None:
            return Response_(
                response=self.body, status=self.status, headers=self.headers,
                mimetype=self.mimetype
            )

        return Response_(
            response=self.body, status=self.status, headers=self.headers,
            content_type=f'{self.mimetype}; charset={self.charset}'
        )

    def convert(self, *exceptions: Exception) -> Response:
        """Prepares the response to convert the specified
        exceptions to itself when exiting a context.
        """
        self._exceptions = exceptions
        return self


class PlainText(Response):  # pylint: disable=R0901
    """Returns a successful plain text response."""

    def __init__(
            self,
            msg: Message = '',
            status: int = 200,
            *,
            charset: str = 'utf-8',
            headers: dict = None
    ):
        super().__init__(
            msg, status, mimetype='text/plain', charset=charset, encoding=True,
            headers=headers
        )


class Error(Response):
    """An WSGI error message."""

    def __init__(
            self,
            msg: Message = '',
            status: int = 400,
            *,
            charset: str = 'utf-8',
            headers: dict = None
    ):
        if 400 <= status < 600:
            super().__init__(msg, status, charset=charset, headers=headers)
        else:
            raise ValueError(f'Not an error status: {status}')


class OK(Response):
    """Returns a successful plain text response."""

    def __init__(
            self,
            msg: Message = '',
            status: int = 200,
            *,
            charset: str = 'utf-8',
            headers: dict = None
    ):
        if 200 <= status < 300:
            super().__init__(msg, status, charset=charset, headers=headers)
        else:
            raise ValueError(f'Not a success status: {status}')


class HTML(Response):
    """Returns a successful plain text response."""

    def __init__(
            self,
            msg: Any = '',
            status: int = 200,
            *,
            charset: str = 'utf-8',
            headers: dict = None
    ):
        try:
            msg = tostring(msg, encoding=charset, method='html')
        except AttributeError:
            encoding = None
        else:
            encoding = False

        super().__init__(
            msg, status, mimetype='text/html', charset=charset,
            encoding=encoding, headers=headers
        )


class XML(Response):
    """An XML response."""

    def __init__(
            self,
            msg: Any,
            status: int = 200,
            *,
            charset: str = 'utf-8',
            headers: dict = None
    ):
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
            msg, status, mimetype='application/xml', charset=charset,
            encoding=encoding, headers=headers
        )


class JSON(Response):
    """A JSON response."""

    def __init__(
            self,
            json: Any,
            status: int = 200,
            *,
            indent: int = None,
            headers: dict = None,
            preprocess: Optional[Callable[[Any], Any]] = htmlescape
    ):
        if preprocess is not None:
            json = preprocess(json)

        super().__init__(
            jsonify(json, indent=indent), status, mimetype='application/json',
            encoding=True, headers=headers
        )


class Binary(Response):
    """A binary reply."""

    def __init__(
            self,
            msg: bytes,
            status: int = 200,
            *,
            etag: ETag = None,
            filename: str = None,
            headers: dict = None
    ):
        super().__init__(
            msg, status, mimetype=get_mimetype(msg), charset=None,
            encoding=False, headers=headers
        )
        self.etag = etag
        self.filename = filename

    @property
    def response_checksum(self):
        """Returns the SHA-256 checksum of the response."""
        if self.response:
            return sha256(self.body).hexdigest()

        raise ValueError('No response available to hash.')

    @property
    def etag(self):
        """Returns the e-tag."""
        return self.headers.get('ETag')

    @etag.setter
    def etag(self, etag: Union[None, bool, str]):
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

        if (match := fullmatch(CD_REGEX, content_disposition)) is None:
            return None

        _, filename = match.groups()
        return filename

    @filename.setter
    def filename(self, filename: Optional[str]):
        """Sets the file name.

        Setting the file name to None will also remove
        any Content-Disposition header field.
        """
        if filename is None:
            self.headers.pop('Content-Disposition', None)
        else:
            content_disposition = f'attachment; filename="{filename}"'
            self.headers['Content-Disposition'] = content_disposition


class InternalServerError(Error):
    """Indicate internal server errors."""

    def __init__(
            self,
            msg: Message = 'Internal Server Error.',
            *,
            charset: str = 'utf-8',
            headers: dict = None
    ):
        super().__init__(msg, 500, charset=charset, headers=headers)
