"""Representational State Transfer."""

from collections import namedtuple
from functools import lru_cache, partial
from itertools import zip_longest

from wsgilib.common import Error, RequestHandler, WsgiApp
from wsgilib.exceptions import InvalidPlaceholderType, InvalidNodeType, \
    NodeMismatch, UnconsumedPath, PathMismatch, UnmatchedPath
from wsgilib.misc import pathinfo, iterpath

__all__ = [
    'load_handler',
    'Route',
    'Router',
    'RestApp',
    'RestHandler']


PLACEHOLDER_TYPES = {
    'str': str,
    'int': int,
    'bool': bool,
    'float': float}

RoutePlaceholder = namedtuple('RoutePlaceholder', ('name', 'typ', 'optional'))
RouteVariable = namedtuple('RouteVariable', ('name', 'value'))


def load_handler(router, environ, unquote=True, logger=None):
    """Loads the respective resource handler from the provided pool."""

    try:
        return router.match(pathinfo(environ))(
            environ, unquote=unquote, logger=logger)
    except UnmatchedPath as mismatch:
        raise Error('Service not found: {}.'.format(mismatch), status=404)


class Route:
    """A ReST API route.

    A Route is a URL path that may contain
    mandatory or optional placeholders.

    Mandatory placeholders:
        /some/path/<mandatory_placeholder>/to/resource

    Optional placeholders:
        /some/path/[optional_placeholder]

    Placeholders can specify their type:
        placeholder = <name>[:<type>]

    Current supported types are str, int, float and bool.

    Example:
        Route('/my_app/<foo:int>/[frobnicate:bool]')
        Route('/set_name/<name>')
    """

    def __init__(self, path):
        """Sets the respective nodes."""
        self.path = path

    def __str__(self):
        """Returns the path."""
        return self.path

    def __hash__(self):
        """Hashes the route by its path."""
        return hash((self.__class__, self.path))

    def __iter__(self):
        """Yields the respective nodes."""
        for node in iterpath(self.path):
            placeholder = None
            optional = False

            if node.startswith('<') and node.endswith('>'):
                placeholder = node[1:-1]

            if node.startswith('[') and node.endswith(']'):
                placeholder = node[1:-1]
                optional = True

            if placeholder is not None:
                try:
                    placeholder, typ = placeholder.split(':')
                except ValueError:
                    typ = None
                else:
                    try:
                        typ = PLACEHOLDER_TYPES[typ]
                    except KeyError:
                        raise InvalidPlaceholderType(typ) from None

                yield RoutePlaceholder(placeholder, typ, optional)
            else:
                yield node

    def match(self, path):
        """Matches the route against the given path."""
        try:
            return tuple(self.match_items(iterpath(path)))
        except NodeMismatch as node_mismatch:
            raise PathMismatch('Invalid node: "{}".'.format(node_mismatch))
        except InvalidNodeType as invalid_node:
            raise PathMismatch('Invalid node: "{}".'.format(invalid_node))
        except UnconsumedPath as unconsumed:
            raise PathMismatch('Unmatched remainder: "{}".'.format(
                unconsumed))

    def match_items(self, path_nodes):
        """Matches path items."""
        unconsumed = []

        for path_node, route_node in zip_longest(path_nodes, self):
            if route_node is None:
                # Consume supoerfluous path nodes.
                unconsumed.append(path_node)
                continue

            if isinstance(route_node, str):
                if path_node != route_node:
                    raise NodeMismatch(route_node, path_node)
            else:
                name, typ, optional = route_node

                if path_node is None:
                    if optional:
                        yield RouteVariable(name, None)
                    else:
                        raise NodeMismatch(route_node, path_node)
                elif typ is None:
                    yield RouteVariable(name, path_node)
                else:
                    try:
                        value = typ(path_node)
                    except (TypeError, ValueError):
                        raise InvalidNodeType(name, typ, path_node)
                    else:
                        yield RouteVariable(name, value)

        if unconsumed:
            raise UnconsumedPath(unconsumed)


class Router:
    """A ReST router.

    The router matches routes against a
    given path until a match is found.
    Raises UnmatchedPath if no match could be found.
    """

    def __init__(self, *routes):
        """Sets the routes."""
        self.routes = routes

    def match(self, path):
        """Gets the matching route for the respective path."""
        for route, handler in self.routes:
            try:
                args = route.match(path)
            except NodeMismatch:
                continue
            else:
                return partial(handler, args)

        raise UnmatchedPath(path)


class RestHandler(RequestHandler):
    """Handles a certain resource."""

    def __init__(self, args, environ, unquote=True, logger=None):
        """Invokes the super constructor and sets resource."""
        super().__init__(environ, unquote=unquote, logger=logger)
        self.args = args

    @property
    @lru_cache(maxsize=1)
    def resource(self):
        """Returns the primary resource (legacy)."""
        try:
            return self.args[0]
        except IndexError:
            return None

    @property
    @lru_cache(maxsize=1)
    def vars(self):
        """Returns the arguments as a dictionary."""
        return dict(self.args)


class RestApp(WsgiApp):
    """A RESTful web application."""

    def __init__(self, router, unquote=True, cors=None, debug=False):
        """Sets request handler, unquote and CORS flags and debug mode."""
        super().__init__(None, unquote=unquote, cors=cors, debug=debug)
        self.router = router

    @property
    def request_handler(self):
        """Dynamically returns the respective resource handler."""
        return partial(load_handler, self.router)

    @request_handler.setter
    def request_handler(self, router):
        """Ignores setting of request_handler
        to comply with superclass __init__.
        """
        pass
