from django.db import models
from .stackOverflowSnippets import classes_in_module as classes_in_module_without_checking_all
from django.core import exceptions
from sys import stderr


def classes_in_module_from_all(module):
    if hasattr(module, '__all__'):
        return [
            cls
            for cls in [
                getattr(module, cls)
                for cls in module.__all__
                if hasattr(module, cls)
            ]
            if isinstance(cls, type)
        ]
    else:
        return []


def classes_in_module(module):
    return list(set(
        list(classes_in_module_from_all(module))
        +
        list(classes_in_module_without_checking_all(module))
    ))


def only_models(user_made_models):
    return [model for model in user_made_models if models.Model in model.__mro__]


def is_abstract(clazz):
    try:
        return clazz.Meta.abstract
    except BaseException:
        return False


def discard_abstract_models(user_made_models):
    return [model for model in user_made_models if not is_abstract(model)]


def registrable_models_in_module(module):
    return discard_abstract_models(only_models(classes_in_module(module)))


def register_for_me(admin, models_module):
    for model in registrable_models_in_module(models_module):
        try:
            admin.site.register(model)
        except exceptions.ImproperlyConfigured:
            pass
        except BaseException as e:
            print(f'{e.__class__.__name__}: {e}', file=stderr)
