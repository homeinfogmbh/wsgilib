"""Convenience functions."""

from flask import request


__all__ = ['get_bool']


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


def get_bool(key: str, default: bool = False) -> bool:
    """Returns a boolean from the request args."""

    try:
        value = request.args[key]
    except KeyError:
        return default

    try:
        return BOOL_STRINGS[value.lower()]
    except KeyError:
        raise ValueError(f'Not a boolean: {value}') from None
