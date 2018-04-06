import logging
from collections import namedtuple
import json

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


class BaseHandler(object):

    def __init__(self, portal_function):
        self.portal_function = portal_function

    def _call_function(self, input_data):

        try:
            output_data = self.portal_function(**input_data)
        except InvalidArgumentsError as e:
            return Response(400, {'error': 'Invalid arguments were passed.'})
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

        return Response(200, output_data)

    def _render_response(self, response):
        status_code = response.status_code
        try:
            body = json.dumps(response.data)
        except Exception:
            logger.exception(
                'Error serialising output from function {} as JSON'
                .format(self.portal_function.name)
            )
            status_code = 500
            body = json.dumps({'error': 'Internal server error.'})
        return body, status_code


class FlaskHandler(BaseHandler):

    def __call__(self):

        # get_json will raise a BAD REQUEST exception if parsing fails
        try:
            inputs = request.get_json(force=True)
        except BadRequest:
            inputs = {}

        response = self._call_function(inputs)
        body, status_code = self._render_response(response)

        return FlaskResponse(
            body, status=status_code, mimetype='application/json'
        )


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
