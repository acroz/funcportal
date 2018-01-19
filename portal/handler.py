import logging

from flask import request, jsonify
from werkzeug.exceptions import (
    HTTPException, BadRequest, InternalServerError, default_exceptions
)
from portal.function import InvalidArgumentsError, MissingArgumentsError


logger = logging.getLogger(__name__)


class FlaskHandler(object):

    def __init__(self, portal_function):
        self.portal_function = portal_function

    @property
    def name(self):
        return self.portal_function.name

    def __call__(self):

        # get_json will raise a BAD REQUEST exception if parsing fails
        try:
            inputs = request.get_json(force=True)
        except BadRequest:
            inputs = {}

        try:
            output = self.portal_function(**inputs)
        except InvalidArgumentsError as e:
            raise BadRequest('Invalid arguments were passed.')
        except MissingArgumentsError as e:
            response = jsonify({
                'error': True,
                'description': str(e),
                'arguments': self.portal_function.describe_arguments()
            })
            response.status_code = 400
            return response
        except Exception:
            logger.exception(
                'An error occurred while evaluating the function {}'
                .format(self.name)
            )
            raise InternalServerError()

        try:
            return jsonify(output)
        except TypeError:
            logger.exception(
                'An error occurred while serialising the return value from ' +
                'the function {}'.format(self.name)
            )
            raise InternalServerError()


def configure_flask_app(app):
    for exception_type in default_exceptions.values():
        app.register_error_handler(exception_type, _flask_json_errorhandler)


def _flask_json_errorhandler(exception):
    """Create a JSON-encoded flask Response from an Exception."""

    if not isinstance(exception, HTTPException):
        exception = InternalServerError()

    response = jsonify({
        'error': True,
        'name': exception.name,
        'description': exception.description
    })
    response.status_code = exception.code

    return response
