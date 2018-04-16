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


class BaseHandler(object):

    def __init__(self, portal_function):
        self.portal_function = portal_function

    def _call_and_catch_errors(self, callable):
        try:
            return callable()
        except InvalidArgumentsError:
            return Response(
                400, {'error': 'Invalid arguments were passed.'}
            )
        except MissingArgumentsError as e:
            data = {
                'error': str(e),
                'arguments': _describe_arguments(
                    self.portal_function.arguments
                )
            }
            return Response(400, data)
        except Exception:
            logger.exception(
                'Error evaluating the function {}'
                .format(self.portal_function.name)
            )
            return Response(500, {'error': 'Internal server error.'})

    @handle_errors
    def _call_function(self, input_data):
        return Response(200, {'result': self.portal_function(**input_data)})


class FlaskHandler(BaseHandler):

    def __call__(self):

        # get_json will raise a BAD REQUEST exception if parsing fails
        try:
            inputs = request.get_json(force=True)
        except BadRequest:
            inputs = {}

        response = self._call_function(inputs)

        body, status = render_response(response, self.portal_function.name)
        return FlaskResponse(body, status=status, mimetype='application/json')


class BaseQueueHandler(BaseHandler):

    def __init__(self, portal_function, queue):
        super(BaseQueueHandler, self).__init__(portal_function)
        self.queue = queue

    def _submit_function(self, input_data):
        return self._call_and_catch_errors(
            lambda: Response(
                202,
                {'job_id': self.portal_function.submit(
                    self.queue, **input_data
                )}
            )
        )


class FlaskQueueSubmissionHandler(BaseQueueHandler):

    def __call__(self):

        # get_json will raise a BAD REQUEST exception if parsing fails
        try:
            inputs = request.get_json(force=True)
        except BadRequest:
            inputs = {}

        response = self._submit_function(inputs)

        body, status = render_response(response, self.portal_function.name)
        return FlaskResponse(body, status=status, mimetype='application/json')


class FlaskQueueRetrievalHandler(BaseQueueHandler):

    def __call__(self, job_id):

        job = self.queue.fetch_job(job_id)
        if job is None:
            response = Response(404, {'error': 'No such job.'})
        if job.result is None:
            response = Response(404, {'error': 'Job result not available.'})
        else:
            output_data = job.result
            response = Response(200, {'result': output_data})

        body, status = render_response(response, self.portal_function.name)
        return FlaskResponse(body, status=status, mimetype='application/json')


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
