"""Decorators for WSGI functions."""

from functools import wraps
from typing import Any, Callable

from flask import request

from wsgilib.exceptions import InvalidData


__all__ = ['require_json']


AnyFunc = Callable[..., Any]


def require_json(typ: type) -> Callable[[AnyFunc], AnyFunc]:
    """Checks for valid JSON data."""

    def decorator(function: AnyFunc) -> AnyFunc:
        """Decorates the function."""
        @wraps(function)
        def wrapper(*args, **kwargs) -> Any:
            """Wraps the original function."""
            if isinstance(request.json, typ):
                return function(*args, **kwargs)

            raise InvalidData(typ, type(request.json))

        return wrapper

    return decorator
