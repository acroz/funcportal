import six

if six.PY3:
    from inspect import signature, Parameter
else:
    from funcsigs import signature, Parameter


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


class PortalFunction(object):

    def __init__(self, function):
        self.function = function

        sig = signature(self.function)
        self.parameters = sig.parameters.values()

        self.required_parameters = []
        self.optional_parameters = []
        for param in self.parameters:
            if param.default is Parameter.empty:
                self.required_parameters.append(param)
            else:
                self.optional_parameters.append(param)

    @property
    def name(self):
        return self.function.__name__

    def describe_arguments(self):
        return {
            'required': [
                {'name': param.name}
                for param in self.required_parameters
            ],
            'optional': [
                {'name': param.name, 'default': param.default}
                for param in self.optional_parameters
            ]
        }

    def _check_arguments(self, **kwargs):
        required = set(param.name for param in self.parameters
                       if param.default is Parameter.empty)
        provided = set(kwargs.keys())

        missing = required - provided
        extra = provided - required

        if missing:
            raise MissingArgumentsError(self.name, missing)
        if extra:
            pass

    def __call__(self, **kwargs):
        self._check_arguments(**kwargs)
        return self.function(**kwargs)
