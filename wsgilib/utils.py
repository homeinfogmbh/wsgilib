"""Additional utilities."""

from datetime import timedelta
from functools import update_wrapper

from flask import make_response, request, current_app


__all__ = ['crossdomain']

__credits__ = 'http://flask.pocoo.org/snippets/56/'


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    """Adds CORS headers to the response of the respective fucntion."""

    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        """Returns the configured HTTP methods."""
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(function):
        """Decorates the respective function."""
        def wrapped_function(*args, **kwargs):
            """Wraps the respective function."""
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(function(*args, **kwargs))

            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            resp.headers['Access-Control-Allow-Origin'] = origin
            resp.headers['Access-Control-Allow-Methods'] = get_methods()
            resp.headers['Access-Control-Max-Age'] = str(max_age)

            if headers is not None:
                resp.headers['Access-Control-Allow-Headers'] = headers

            return resp

        function.provide_automatic_options = False
        return update_wrapper(wrapped_function, function)

    return decorator
