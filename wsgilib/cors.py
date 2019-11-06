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
    def allow_origin(self):
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
    def methods(self):
        """Returns the allowed CORS methods."""
        try:
            return self['methods']
        except KeyError:
            return METHODS

    @property
    def headers(self):
        """Returns the to-be-set CORS headers."""
        try:
            return self['headers']
        except KeyError:
            return HEADERS

    def apply(self, headers):
        """Applies CORS settings to the respective headers."""
        try:
            headers.add('Access-Control-Allow-Origin', self.allow_origin)
        except NoOriginError:
            LOGGER.warning('Request did not specify any origin.')
            return headers
        except UnauthorizedOrigin:
            LOGGER.warning('Request from unauthorized origin.')
            return headers

        if self.get('credentials'):
            headers.add('Access-Control-Allow-Credentials', 'true')

        for header in self.headers:
            headers.add('Access-Control-Allow-Headers', header)

        headers.add('Access-Control-Allow-Methods', ', '.join(self.methods))
        return headers
