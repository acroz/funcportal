import logging
from collections import namedtuple
import json
from functools import wraps

from flask import request, Response as FlaskResponse
from werkzeug.exceptions import (
    HTTPException, BadRequest, InternalServerError, default_exceptions
)
from funcportal.function import InvalidArgumentsError, MissingArgumentsError


logger = logging.getLogger(__name__)


Response = namedtuple('Response', ['status_code', 'data'])


def _describe_arguments(arguments):
    return {
        'required': [
            {'name': arg.name} for arg in arguments if arg.required
        ],
        'optional': [
            {'name': arg.name, 'default': arg.default}
            for arg in arguments if not arg.required
        ]
    }


def handle_errors(handler_method):

    @wraps(handler_method)
    def wrapped(obj, *args, **kwargs):
        try:
            return handler_method(obj, *args, **kwargs)
        except InvalidArgumentsError:
            return Response(
                400, {'error': 'Invalid arguments were passed.'}
            )
        except MissingArgumentsError as e:
            data = {
                'error': str(e),
                'arguments': _describe_arguments(
                    obj.portal_function.arguments
                )
            }
            return Response(400, data)
        except Exception:
            logger.exception(
                'Error evaluating the function {}'
                .format(obj.portal_function.name)
            )
            return Response(500, {'error': 'Internal server error.'})

    return wrapped


class BaseHandler(object):

    def __init__(self, portal_function):
        self.portal_function = portal_function

    @handle_errors
    def _call_function(self, input_data):
        return Response(200, {'result': self.portal_function(**input_data)})


class BaseQueueHandler(BaseHandler):

    def __init__(self, portal_function, queue):
        super(BaseQueueHandler, self).__init__(portal_function)
        self.queue = queue

    @handle_errors
    def _submit_function(self, input_data):
        return Response(
            202,
            {'result_token':
                self.portal_function.submit(self.queue, **input_data)}
        )


def render_response(response, function_name):
    status_code = response.status_code
    try:
        body = json.dumps(response.data)
    except Exception:
        logger.exception(
            'Error serialising output from function {} as JSON'
            .format(function_name)
        )
        status_code = 500
        body = json.dumps({'error': 'Internal server error.'})
    return body, status_code


def render_flask_response(response, function_name):
    body, status = render_response(response, function_name)
    return FlaskResponse(body, status=status, mimetype='application/json')


class FlaskHandler(BaseHandler):

    def __call__(self):
        if self.portal_function.requires_arguments():
            try:
                inputs = request.get_json(force=True)
            except BadRequest:
                return render_flask_response(
                    Response(400, {'error': 'Malformatted JSON.'}),
                    self.portal_function.name
                )
        else:
            inputs = {}

        response = self._call_function(inputs)
        return render_flask_response(response, self.portal_function.name)


class FlaskQueueSubmissionHandler(BaseQueueHandler):

    def __call__(self):

        if self.portal_function.requires_arguments():
            try:
                inputs = request.get_json(force=True)
            except BadRequest:
                return render_flask_response(
                    Response(400, {'error': 'Malformatted JSON.'}),
                    self.portal_function.name
                )
        else:
            inputs = {}

        response = self._submit_function(inputs)
        return render_flask_response(response, self.portal_function.name)


class FlaskQueueRetrievalHandler(BaseQueueHandler):

    def __call__(self, result_token):

        job = self.queue.fetch_job(result_token)

        if job is None:
            response = Response(404, {'error': 'No such job.'})
        if job.result is None:
            response = Response(404, {'error': 'Job result not available.'})
        else:
            output_data = job.result
            response = Response(200, {'result': output_data})

        return render_flask_response(response, self.portal_function.name)


def configure_flask_app(app):
    for exception_type in default_exceptions.values():
        app.register_error_handler(exception_type, _flask_json_errorhandler)


def _flask_json_errorhandler(exception):
    """Create a JSON-encoded flask Response from an Exception."""

    if not isinstance(exception, HTTPException):
        exception = InternalServerError()

    body = json.dumps({
        'error': exception.name,
        'description': exception.description
    })
    status_code = exception.code

    return FlaskResponse(body, status=status_code, mimetype='application/json')
