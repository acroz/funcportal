import logging

from flask import request, jsonify
from werkzeug.exceptions import BadRequest, InternalServerError
from portal.function import InvalidArguments

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
        except InvalidArguments:
            raise BadRequest('invalid arguments were passed')
        except:
            raise InternalServerError('internal server error')

        try:
            return jsonify(output)
        except TypeError:
            logger.exception(
                'An error occurred while serialising the return value from ' +
                'the function {}'.format(self.name)
            )
            raise InternalServerError('internal server error')
