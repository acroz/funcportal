from flask import Flask

from funcportal.function import PortalFunction
from funcportal.handler import FlaskHandler, configure_flask_app


class Portal(object):

    def __init__(self):
        self.routes = {}

    def register_endpoint(self, endpoint, function):
        self.routes[endpoint] = PortalFunction(function)

    def generate_wsgi_app(self):
        app = Flask('funcportal')
        configure_flask_app(app)
        for endpoint, function in self.routes.items():
            handler = FlaskHandler(function)
            # TODO: Consider allowing GET for functions without arguments
            app.add_url_rule(
                endpoint, endpoint, handler, methods=['POST']
            )
        return app

    def run_wsgi(self):
        # TODO: Use gunicorn
        wsgi_app = self.generate_wsgi_app()
        wsgi_app.run()
