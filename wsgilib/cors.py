"""Cross-origin resource sharing."""

from logging import getLogger
from typing import Iterator, List, Set

from flask import request
from werkzeug.datastructures import Headers

from wsgilib.types import Header


__all__ = ['NoOriginError', 'UnauthorizedOrigin', 'CORS']


ANY = '*'
LOGGER = getLogger('wsgilib.cors')


class NoOriginError(Exception):
    """Indidates that the request did not send an origin field."""


class UnauthorizedOrigin(Exception):
    """Indicates that the origin is not authorized."""


class CORS(dict):
    """CORS settings."""

    @property
    def allowed_origins(self) -> Set[str]:
        """Returns the configured origins, defaulting to '*'."""
        try:
            return set(self['origins'])
        except KeyError:
            return {ANY}

    @property
    def allowed_methods(self) -> List[str]:
        """Yields the allowed CORS methods."""
        try:
            return self['methods']
        except KeyError:
            return [ANY]

    @property
    def allowed_headers(self) -> List[str]:
        """Yields the to-be-set CORS headers."""
        try:
            return self['headers']
        except KeyError:
            return [ANY]

    @property
    def allowed_origin(self) -> str:
        """Returns the allow origin value."""
        if ANY in self.allowed_origins:
            try:
                return request.headers['origin']
            except KeyError:
                return ANY

        origin = request.headers.get('origin')

        if not origin:
            raise NoOriginError()

        if origin in self.allowed_origins:
            return origin

        raise UnauthorizedOrigin()

    @property
    def headers(self) -> Iterator[Header]:
        """Yields the CORS headers."""
        try:
            yield ('Access-Control-Allow-Origin', self.allowed_origin)
        except NoOriginError:
            LOGGER.warning('Request did not specify any origin.')
            return
        except UnauthorizedOrigin:
            LOGGER.warning('Request from unauthorized origin.')
            return

        if self.get('credentials'):
            yield ('Access-Control-Allow-Credentials', 'true')

        for allowed_header in self.allowed_headers:
            yield ('Access-Control-Allow-Headers', allowed_header)

        yield ('Access-Control-Allow-Methods', ', '.join(self.allowed_methods))

    def apply(self, headers: Headers) -> None:
        """Applies CORS settings to a headers object."""
        for header, value in self.headers:
            headers.add(header, value)
