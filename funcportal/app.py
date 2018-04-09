from collections import namedtuple

from flask import Flask
import yaml

from funcportal import util
from funcportal.function import PortalFunction
from funcportal.handler import FlaskHandler, configure_flask_app


Route = namedtuple('Route', ['module', 'function', 'endpoint'])


class ConfigurationError(RuntimeError):
    pass


class Portal(object):

    def __init__(self):
        self.routes = {}

    def load_config(self, path):

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

        self.from_routes(routes)

    @classmethod
    def from_routes(cls, routes):
        portal = cls()
        for route in routes:
            function = util.import_function(route.module, route.function)
            portal.register_endpoint(route.endpoint, function)
        return portal

    def register_endpoint(self, endpoint, function):
        self.routes[endpoint] = PortalFunction(function)

    def generate_wsgi_app(self):
        app = Flask('funcportal')
        configure_flask_app(app)
        for endpoint, function in self.routes.items():
            handler = FlaskHandler(function)
            # TODO: Consider allowing GET for functions without arguments
            app.add_url_rule(
                endpoint, function.name, handler, methods=['POST']
            )
        return app

    def run_wsgi(self):
        # TODO: Use gunicorn
        wsgi_app = self.generate_wsgi_app()
        wsgi_app.run()
