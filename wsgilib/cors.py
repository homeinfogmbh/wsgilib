"""Cross-origin resource sharing."""

from flask import request


__all__ = ['METHODS', 'HEADERS', 'NoOriginError', 'UnauthorizedOrigin', 'CORS']


METHODS = ['GET', 'OPTIONS', 'PATCH', 'POST', 'PUT', 'DELETE']
HEADERS = [
    'Content-Type',
    'Cache-Control',
    'X-Requested-With',
    'Authorization'
]


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
            allowed_origins = '*'

        if allowed_origins == '*':
            return '*'

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
        headers.add('Access-Control-Allow-Origin', self.allow_origin)

        if self.get('credentials'):
            headers.add('Access-Control-Allow-Credentials', 'true')

        for header in self.headers:
            headers.add('Access-Control-Allow-Headers', header)

        headers.add('Access-Control-Allow-Methods', ', '.join(self.methods))
