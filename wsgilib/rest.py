"""Representational State Transfer."""

from collections import namedtuple
from functools import lru_cache, partial
from itertools import chain

from wsgilib.common import Error, RequestHandler, WsgiApp
from wsgilib.exceptions import InvalidPlaceholderType, InvalidNodeType, \
    NodeMismatch, UnconsumedPath, PathMismatch, UnmatchedPath
from wsgilib.misc import PATH_SEP, PLACEHOLDER_TYPES, pathinfo, iterpath

__all__ = [
    'load_handler',
    'Route',
    'RestApp',
    'RestHandler']

RoutePlaceholder = namedtuple('RoutePlaceholder', ('name', 'typ'))
RouteVariable = namedtuple('RouteVariable', ('name', 'value'))


def load_handler(router, environ, unquote=True, logger=None):
    """Loads the respective resource handler from the provided pool."""

    try:
        return router.match(pathinfo(environ))(
            environ, unquote=unquote, logger=logger)
    except UnmatchedPath as mismatch:
        raise Error('Service not found: {}.'.format(mismatch), status=404)


class Router:
    """A ReST router."""

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


class Route:
    """A ReST API route."""

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
            if node.startswith('<') and node.endswith('>'):
                placeholder = node[1:-1]

                try:
                    placeholder, typ = placeholder.split(':')
                except ValueError:
                    typ = None
                else:
                    try:
                        typ = PLACEHOLDER_TYPES[typ]
                    except KeyError:
                        raise InvalidPlaceholderType(typ)

                yield RoutePlaceholder(placeholder, typ)
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
        for path_node, route_node in zip(path_nodes, self):
            print('Path node:', path_node)
            if isinstance(route_node, str):
                if path_node != route_node:
                    raise NodeMismatch(route_node, path_node)
            else:
                name, typ = route_node

                if typ is None:
                    yield RouteVariable(name, path_node)
                else:
                    try:
                        value = typ(path_node)
                    except (TypeError, ValueError):
                        raise InvalidNodeType(name, typ, path_node)
                    else:
                        yield RouteVariable(name, value)

        try:
            tail = (path_node,)
        except UnboundLocalError:
            tail = ()

        remainder = PATH_SEP.join(chain(path_nodes, tail))

        if remainder:
            raise UnconsumedPath(remainder)


class RestHandler(RequestHandler):
    """Handles a certain resource."""

    def __init__(self, args, environ, unquote=True, logger=None):
        """Invokes the super constructor and sets resource."""
        super().__init__(environ, unquote=unquote, logger=logger)
        self.args = args

    def __getitem__(self, item):
        """Returns sub-handlers or pools."""
        raise KeyError('No such sub-handler or pool: {}.'.format(item))

    @property
    def resource(self):
        """Returns the primary resource (legacy)."""
        try:
            return self.args[0]
        except IndexError:
            return None

    @property
    @lru_cache(maxsize=1)
    def keys(self):
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
