#  wsgilib
#  Copyright (C) 2017  HOMEINFO - Digitale Informationssysteme GmbH
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
"""Exceptions for the WSGI library."""

from wsgilib.misc import PATH_SEP


__all__ = [
    'RouteError',
    'InvalidPlaceholderType',
    'InvalidNodeType',
    'NodeMismatch',
    'UnconsumedPath',
    'PathMismatch',
    'UnmatchedPath']


class RouteError(Exception):
    """Base exception for errors concerning ReST routes."""

    pass


class InvalidPlaceholderType(RouteError):
    """Indicates that an unsupported
    placeholder type has been specified.
    """

    def __init__(self, typ):
        """Sets the respective type name."""
        super().__init__(typ)
        self.typ = typ

    def __str__(self):
        """Returns the type name."""
        return self.typ


class InvalidNodeType(RouteError):
    """Indicates that an invalid value for a
    node placeholder has been encountered.
    """

    def __init__(self, name, typ, value):
        """Sets the respective type name."""
        super().__init__(name, typ, value)
        self.name = name
        self.typ = typ
        self.value = value

    def __str__(self):
        """Returns the type name."""
        return 'Invalid value "{}" for node "{}" of type "{}".'.format(
            self.value, self.name, self.typ)


class NodeMismatch(RouteError):
    """Indicates that an unexpected route node has been encountered."""

    def __init__(self, expected, encountered):
        """Sets the expected and encountered path node."""
        super().__init__(expected, encountered)
        self.expected = expected
        self.encountered = encountered

    def __str__(self):
        """Returns the appropriate warning message."""
        return 'Expected node "{}", but encountered "{}".'.format(
            self.expected, self.encountered)


class UnconsumedPath(RouteError):
    """Indicates that there are unconsumed path nodes."""

    def __init__(self, remainder):
        """Sets the remainder."""
        super().__init__(remainder)
        self.remainder = remainder

    def __str__(self):
        """Returns the remainder as path."""
        return self.remainder


class PathMismatch(RouteError):
    """Indicates that the path does not match the respective route."""

    def __init__(self, message):
        """Sets the respective message."""
        super().__init__(message)
        self.message = message

    def __str__(self):
        """Returns the respective message."""
        return self.message


class UnmatchedPath(RouteError):
    """Indicates that the respective path is not matched by any route."""

    def __init__(self, path):
        """Sets the respective path."""
        super().__init__(path)
        self.path = path

    def __str__(self):
        """Returns the path."""
        return self.path
