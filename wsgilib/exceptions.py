# Copyright 2017 HOMEINFO - Digitale Informationssysteme GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
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

    def __init__(self, nodes):
        """Sets the remaining nodes."""
        super().__init__(nodes)
        self.nodes = tuple(nodes)

    def __str__(self):
        """Returns the remainder as path."""
        return PATH_SEP.join(self.nodes)


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
