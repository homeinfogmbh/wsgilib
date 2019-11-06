"""Cross-origin resource sharing."""

from logging import getLogger

from flask import request


__all__ = ['METHODS', 'HEADERS', 'NoOriginError', 'UnauthorizedOrigin', 'CORS']


ANY = '*'
METHODS = ['GET', 'OPTIONS', 'PATCH', 'POST', 'PUT', 'DELETE']
HEADERS = [
    'Content-Type',
    'Cache-Control',
    'X-Requested-With',
    'Authorization'
]
LOGGER = getLogger('wsgilib.cors')


class NoOriginError(Exception):
    """Indidates that the request did not send an origin field."""


class UnauthorizedOrigin(Exception):
    """Indicates that the origin is not authorized."""


class CORS(dict):
    """CORS settings."""

    @property
    def allowed_origins(self):
        """Returns the allow origin value."""
        try:
            allowed_origins = self['origins']
        except KeyError:
            allowed_origins = ANY

        if allowed_origins == ANY:
            try:
                return request.headers['origin']
            except KeyError:
                return ANY

        origin = request.headers.get('origin')

        if not origin:
            raise NoOriginError()

        if origin in allowed_origins:
            return origin

        raise UnauthorizedOrigin()

    @property
    def allowed_methods(self):
        """Yields the allowed CORS methods."""
        try:
            yield from self['methods']
        except KeyError:
            yield ANY

    @property
    def allowed_headers(self):
        """Yields the to-be-set CORS headers."""
        try:
            yield from self['headers']
        except KeyError:
            yield ANY

    @property
    def headers(self):
        """Yields the CORS headers."""
        try:
            yield ('Access-Control-Allow-Origin', self.allowed_origins)
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

    def apply(self, headers):
        """Applies CORS settings to the respective headers."""
        for header, value in self.headers:
            headers.add(header, value)

        return headers
