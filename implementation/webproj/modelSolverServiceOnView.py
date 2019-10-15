# -*- encoding: utf-8 -*-

from django.db.models import Model
from django.http import Http404
from typing import Type
from typing import Dict
from typing import Callable


class ModelSolver(object):
    def __init__(self, to_raise: BaseException = Http404(), **kwargs: Dict[str, Type[Model]]):
        assert isinstance(to_raise, BaseException)
        for kw, cls in kwargs.items():
            assert isinstance(kw, str)
            assert issubclass(cls, Model)
        self.t = kwargs
        self.r = to_raise

    def __call__(self, c):
        return ModelSolverConfigured(c, self.r, **self.t)


class ModelSolverConfigured(object):  # Don't instantiate this class manually
    def __init__(self, clb: Callable, to_raise: BaseException = Http404(), **kwargs: Dict[str, Type[Model]]):
        self.r = to_raise  # raise
        self.t = kwargs  # transform
        self.c = clb  # callback

    def __call__(self, *args, **kwargs):
        newkwargs = dict()
        for k, v in kwargs.items():
            if k not in self.t:
                newkwargs[k] = v
            else:
                obj = self.t[k].objects.filter(**{k: v}).first()
                # solved sample: self.[User].objects.filter([username='john']).first() -> Optional[User]
                if obj is None and self.r is not None:
                    raise self.r
                else:
                    newkwargs[k] = obj
        return self.c(*args, **newkwargs)
