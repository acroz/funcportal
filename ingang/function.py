import six

if six.PY3:
    from inspect import signature
else:
    from funcsigs import signature


class InvalidArguments(Exception):
    pass


class IngangFunction(object):

    def __init__(self, function):
        self.function = function

    @property
    def name(self):
        return self.function.__name__

    def _check_arguments(self, **kwargs):
        sig = signature(self.function)
        try:
            sig.bind(**kwargs)
        except TypeError as e:
            raise InvalidArguments(str(e))

    def __call__(self, **kwargs):
        self._check_arguments(**kwargs)
        return self.function(**kwargs)
