import argparse

from ingang.app import Ingang
from ingang import util


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('functions', nargs='+')
    args = parser.parse_args()

    app = Ingang()

    for function_arg in args.functions:
        parts = function_arg.split(':')
        import_path = ':'.join(parts[:2])
        func = util.import_function(import_path)

        try:
            endpoint = parts[2]
        except:
            endpoint = import_path.replace('.', '/').replace(':', '/')
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint

        app.register_endpoint(endpoint, func)

    app.run_wsgi()
