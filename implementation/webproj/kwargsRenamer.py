# -*- encoding: utf-8 -*-

from typing import Callable
from typing import Dict


class KeywordArgumentsRenamer(object):
    def __init__(self, **kwargs_changes: Dict[str, str]):
        for oldkw, newkw in kwargs_changes.items():
            assert isinstance(oldkw, str)
            assert isinstance(newkw, str)
        self.kwargs_changes = kwargs_changes

    def __call__(self, c):
        return KeywordArgumentsRenamerConfigured(c, **self.kwargs_changes)


class KeywordArgumentsRenamerConfigured(object):  # Don't instantiate this class manually
    def __init__(self, clb: Callable, **kwargs_changes: Dict[str, str]):
        self.kwargs_changes = kwargs_changes
        self.callback = clb
    
    def __call__(self, *args, **kwargs):
        newkwargs = {
            self.kwargs_changes[kw] if kw in self.kwargs_changes else kw:
            arg
            for kw, arg
            in kwargs.items()
        }
        return self.callback(*args, **newkwargs)

