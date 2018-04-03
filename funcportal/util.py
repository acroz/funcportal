import os
import sys


class FunctionImportError(Exception):
    pass


def import_function(module, function):
    """Import a function from a module."""

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
        obj = getattr(mod, function)
    except AttributeError:
        tpl = 'Failed to find function {!r} in module {!r}'
        raise FunctionImportError(tpl.format(function, module))

    if not callable(obj):
        raise FunctionImportError('Object is not callable: {!r}'.format(obj))

    return obj
