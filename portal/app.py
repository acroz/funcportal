from flask import Flask

from portal.function import PortalFunction
from portal.handler import FlaskHandler


class Portal(object):

    def __init__(self):
        self.routes = {}

    def register_endpoint(self, route, function):
        self.routes[route] = PortalFunction(function)

    def generate_wsgi_app(self):
        app = Flask('portal')
        for route, function in self.routes.items():
            handler = FlaskHandler(function)
            # TODO: Consider allowing GET for functions without arguments
            app.add_url_rule(route, handler.name, handler, methods=['POST'])
        return app

    def run_wsgi(self):
        # TODO: Use gunicorn
        wsgi_app = self.generate_wsgi_app()
        wsgi_app.run()
