"""Convenience functions."""

from configparser import RawConfigParser

from flask import request


__all__ = ['get_bool']


def get_bool(key: str, *, source: dict = request.args) -> bool:
    """Returns a boolean from the request args or another given source."""

    value = source[key]

    try:
        return RawConfigParser.BOOLEAN_STATES[value.lower()]
    except KeyError:
        raise ValueError(f'Not a boolean: {value}') from None
