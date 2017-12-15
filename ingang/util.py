import os
import sys


class FunctionImportError(Exception):
    pass


def import_function(module):
    """Adapted from gunicorn."""

    parts = module.split(':', 1)

    if len(parts) == 1:
        # Get all callables from module
        module, obj = module, 'application'
    else:
        module, obj = parts[0], parts[1]

    try:
        __import__(module)
    except ImportError:
        if module.endswith('.py') and os.path.exists(module):
            tpl = "Failed to find application, did you mean '{}:{}'?"
            raise ImportError(tpl.format(module.rstrip('.py'), obj))
        else:
            raise

    mod = sys.modules[module]

    try:
        # TODO: Could this eval be replaced with a getattr?
        app = eval(obj, vars(mod))
    except NameError:
        tpl = 'Failed to find application object {!r} in {!r}'
        raise FunctionImportError(tpl.format(obj, module))

    if app is None:
        tpl = 'Failed to find application object: {!r}'
        raise FunctionImportError(tpl.format(obj))

    if not callable(app):
        raise FunctionImportError('Object is not callable: {!r}'.format(app))

    return app
