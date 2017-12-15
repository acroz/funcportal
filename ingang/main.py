import argparse
from collections import namedtuple

from ingang.app import Ingang
from ingang import util


Endpoint = namedtuple('Endpoint', ['module', 'function', 'route'])


FORMAT_ERROR_TEMPLATE = "{!r} does not match format 'module:function[:route]'"


def parse_endpoint(arg):

    parts = arg.split(':')

    try:
        module = parts[0]
        function = parts[1]
    except IndexError:
        raise argparse.ArgumentTypeError(FORMAT_ERROR_TEMPLATE.format(arg))

    if len(module) == 0 or len(function) == 0:
        raise argparse.ArgumentTypeError(FORMAT_ERROR_TEMPLATE.format(arg))

    try:
        route = parts[2]
    except:
        route = '/{}/{}'.format(module.replace('.', '/'), function)

    if not route.startswith('/'):
        route = '/' + route

    return Endpoint(module, function, route)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('endpoints', nargs='+', type=parse_endpoint)
    args = parser.parse_args()

    app = Ingang()

    for endpoint in args.endpoints:
        function = util.import_function(endpoint.module, endpoint.function)
        app.register_endpoint(endpoint.route, function)

    app.run_wsgi()
