import os
import sys


class FunctionImportError(Exception):
    pass


def import_function(module, function):
    """Adapted from gunicorn."""

    try:
        __import__(module)
    except ImportError:
        if module.endswith('.py') and os.path.exists(module):
            tpl = "Failed to find function, did you mean '{}:{}'?"
            raise ImportError(tpl.format(module.rstrip('.py'), function))
        else:
            raise

    mod = sys.modules[module]

    try:
        # TODO: Could this eval be replaced with a getattr?
        obj = eval(function, vars(mod))
    except NameError:
        tpl = 'Failed to find function {!r} in {!r}'
        raise FunctionImportError(tpl.format(obj, module))

    if obj is None:
        tpl = 'Failed to find function: {!r}'
        raise FunctionImportError(tpl.format(function))

    if not callable(obj):
        raise FunctionImportError('Object is not callable: {!r}'.format(obj))

    return obj
