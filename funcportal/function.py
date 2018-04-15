from collections import namedtuple
import six

if six.PY3:
    from inspect import signature, Parameter
else:
    from funcsigs import signature, Parameter


Argument = namedtuple('Argument', ['name', 'required', 'default'])


class MissingArgumentsError(TypeError):

    def __init__(self, function_name, missing_arguments):
        self.missing_arguments = missing_arguments
        message = '{}() missing {} required positional argument{}: {}'.format(
            function_name,
            len(missing_arguments),
            '' if len(missing_arguments) == 1 else 's',
            ', '.join(repr(arg) for arg in missing_arguments)
        )
        super(MissingArgumentsError, self).__init__(message)


class InvalidArgumentsError(Exception):
    pass


def _get_arguments(function):

    sig = signature(function)

    arguments = []

    for parameter in sig.parameters.values():
        required = parameter.default is Parameter.empty
        arguments.append(Argument(parameter.name, required, parameter.default))

    return arguments


class PortalFunction(object):

    def __init__(self, function):
        self.function = function
        self.name = self.function.__name__
        self.arguments = _get_arguments(function)

    def _check_arguments(self, **kwargs):
        required = set(arg.name for arg in self.arguments if arg.required)
        provided = set(kwargs.keys())

        missing = required - provided
        extra = provided - required

        if missing:
            raise MissingArgumentsError(self.name, missing)
        if extra:
            # TODO: Consider logging this case
            pass

    def __call__(self, **kwargs):
        self._check_arguments(**kwargs)
        return self.function(**kwargs)
