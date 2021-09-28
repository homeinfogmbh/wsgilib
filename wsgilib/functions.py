"""Convenience functions to get specific data types from request args."""

from datetime import datetime
from typing import Any, Optional

from flask import request


__all__ = ['get_bool', 'get_datetime', 'get_int']


BOOL_STRINGS = {
    '1': True,
    'yes': True,
    'true': True,
    'on': True,
    '0': False,
    'no': False,
    'false': False,
    'off': False
}


def get_bool(key: str, default: Any = False) -> bool:
    """Returns a boolean from the request args."""

    try:
        value = request.args[key]
    except KeyError:
        return default

    try:
        return BOOL_STRINGS[value.lower()]
    except KeyError:
        raise ValueError('Not a boolean:', key, value) from None


def get_datetime(key: str, default: Any = None) -> Optional[datetime]:
    """Returns a datetime from a URL parameter."""

    try:
        value = request.args[key]
    except KeyError:
        return default

    return datetime.fromisoformat(value)


def get_int(key: str, default: Any = None) -> bool:
    """Returns a boolean from the request args."""

    try:
        value = request.args[key]
    except KeyError:
        return default

    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValueError('Not an int:', key, value) from None
