import argparse
from collections import namedtuple

import yaml

from funcportal.app import Portal, run_async_worker
from funcportal import util


ERROR_TEMPLATE = "{!r} does not match format 'module:function[:endpoint]'"


Route = namedtuple('Route', ['module', 'function', 'endpoint', 'asynchronous'])


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
                entry['module'], entry['function'], entry['endpoint'],
                entry.get('async', False)
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

    return Route(module, function, route, False)


def main():

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command')

    server = subparsers.add_parser('server')
    server.add_argument(
        'routes', nargs='+', type=parse_route,
        help='One or more route definitions, in the format ' +
             'module:function[:endpoint]. If not specified, the route will ' +
             'be the function name.'
    )
    server.add_argument(
        '--config', '-c', help='A YAML configuration file to load'
    )

    subparsers.add_parser('worker')

    args = parser.parse_args()

    if args.command == 'server':

        app = Portal()

        routes = []
        if args.config is not None:
            routes += routes_from_config(args.config)
        routes += args.routes

        for route in routes:
            function = util.import_function(route.module, route.function)
            app.register_endpoint(route.endpoint, function, route.asynchronous)

        app.run_wsgi()

    elif args.command == 'worker':
        run_async_worker()
