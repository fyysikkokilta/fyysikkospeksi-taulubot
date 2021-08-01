import os
import importlib

pyfile_extensions = ['py']

__all__ = []
for filename in [os.path.splitext(i)[0] for i in os.listdir(os.path.dirname(__file__)) if
                 os.path.splitext(i)[1] in pyfile_extensions]:
    if not filename.startswith('__'):
        __all__.append(importlib.import_module('.%s' % filename, __package__))

del os, importlib, pyfile_extensions