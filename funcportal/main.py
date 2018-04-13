import argparse
from collections import namedtuple

import yaml

from funcportal.app import Portal
from funcportal import util


ERROR_TEMPLATE = "{!r} does not match format 'module:function[:endpoint]'"


Route = namedtuple('Route', ['module', 'function', 'endpoint'])


class ConfigurationError(RuntimeError):
    pass


def routes_from_config(path):

    with open(path) as fp:
        config = yaml.load(fp)

    try:
        route_data = config['routes']
    except KeyError:
        raise ConfigurationError(
            'No routes entry in config read from {}'.format(path)
        )

    routes = []

    for entry in route_data:
        try:
            route = Route(
                entry['module'], entry['function'], entry['endpoint']
            )
            routes.append(route)
        except (TypeError, KeyError):
            raise ConfigurationError('Malformed endpoint definition')

    return routes


def parse_route(arg):

    parts = arg.split(':')

    try:
        module = parts[0]
        function = parts[1]
    except IndexError:
        raise argparse.ArgumentTypeError(ERROR_TEMPLATE.format(arg))

    if len(module) == 0 or len(function) == 0:
        raise argparse.ArgumentTypeError(ERROR_TEMPLATE.format(arg))

    try:
        route = parts[2]
    except IndexError:
        route = function

    if not route.startswith('/'):
        route = '/' + route

    return Route(module, function, route)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'routes', nargs='+', type=parse_route,
        help='One or more route definitions, in the format ' +
             'module:function[:endpoint]. If not specified, the route is ' +
             'the function name.'
    )
    parser.add_argument(
        '--config', '-c', help='A YAML configuration file to load'
    )
    args = parser.parse_args()

    app = Portal()

    routes = []
    if args.config is not None:
        routes += routes_from_config(args.config)
    routes += args.routes

    for route in routes:
        function = util.import_function(route.module, route.function)
        app.register_endpoint(route.endpoint, function)

    app.run_wsgi()
