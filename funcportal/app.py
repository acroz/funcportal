from flask import Flask
from redis import Redis
from rq import Queue, Worker

from funcportal.function import PortalFunction
from funcportal.handler import (
    FlaskHandler, FlaskQueueSubmissionHandler, FlaskQueueRetrievalHandler,
    configure_flask_app
)


REDIS_CONNECTION = Redis()
JOB_QUEUE = Queue('funcportal', connection=REDIS_CONNECTION)


def run_async_worker():
    worker = Worker([JOB_QUEUE], connection=REDIS_CONNECTION)
    worker.work()


class Portal(object):

    def __init__(self):
        self.routes = {}
        self._queue = None

    def register_endpoint(self, endpoint, function, asynchronous=False):
        self.routes[endpoint] = (PortalFunction(function), asynchronous)

    def generate_wsgi_app(self):
        app = Flask('funcportal')
        configure_flask_app(app)
        for endpoint, (function, asynchronous) in self.routes.items():
            if asynchronous:
                handler = FlaskQueueSubmissionHandler(function, JOB_QUEUE)
            else:
                handler = FlaskHandler(function)
            app.add_url_rule(
                endpoint, endpoint, handler, methods=['POST']
            )

            if asynchronous:
                result_endpoint = endpoint.rstrip('/') + '/<result_token>'
                result_handler = FlaskQueueRetrievalHandler(
                    function, JOB_QUEUE
                )
                app.add_url_rule(
                    result_endpoint, result_endpoint, result_handler,
                    methods=['GET']
                )

        return app

    def run_wsgi(self):
        # TODO: Use gunicorn
        wsgi_app = self.generate_wsgi_app()
        wsgi_app.run()
