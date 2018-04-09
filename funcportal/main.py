import argparse

from funcportal.app import Portal, Route
from funcportal import util


ERROR_TEMPLATE = "{!r} does not match format 'module:function[:endpoint]'"


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

    if args.config is not None:
        app.load_config(args.config)

    for route in args.routes:
        function = util.import_function(route.module, route.function)
        app.register_endpoint(route.endpoint, function)

    app.run_wsgi()
