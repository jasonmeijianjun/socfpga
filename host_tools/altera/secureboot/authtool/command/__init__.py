import os
import importlib

register_hooks = []

for _basename, _ext in map(os.path.splitext, os.listdir(os.path.dirname(__file__))):
    if _ext == '.py' and _basename != '__init__':
        try:
            _register_hook = getattr(importlib.import_module('.' + _basename, __package__), 'register', None)
            if _register_hook is not None:
                register_hooks.append(_register_hook)
            del _register_hook
        except Exception, _err:
            print str(_err)
            del _err

del _basename, _ext

del importlib
del os
