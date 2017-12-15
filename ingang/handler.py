from flask import request, jsonify
from werkzeug.exceptions import BadRequest, InternalServerError
from ingang.function import InvalidArguments


class FlaskHandler(object):

    def __init__(self, ingang_function):
        self.ingang_function = ingang_function

    @property
    def name(self):
        return self.ingang_function.name

    def __call__(self):

        # get_json will raise a BAD REQUEST exception if parsing fails
        try:
            inputs = request.get_json(force=True)
        except BadRequest:
            inputs = {}

        try:
            output = self.ingang_function(**inputs)
        except InvalidArguments:
            raise BadRequest('invalid arguments were passed')
        except:
            raise InternalServerError('invalid server error')

        # TODO: Catch json serialisation errors
        return jsonify(output)
