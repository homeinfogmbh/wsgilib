"""Convenience functions."""

from configparser import RawConfigParser

from flask import request


__all__ = ['get_bool']


def get_bool(key: str, default: bool = False) -> bool:
    """Returns a boolean from the request args."""

    try:
        value = request.args[key]
    except KeyError:
        return default

    try:
        return RawConfigParser.BOOLEAN_STATES[value.lower()]
    except KeyError:
        raise ValueError(f'Not a boolean: {value}') from None
