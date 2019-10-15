from django.db import models
from .stackOverflowSnippets import classesInModule as classesInModuleWithoutCheckingAll
from django.core import exceptions
from sys import stderr


def classesInModuleFromAll(module):
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


def classesInModule(module):
    return list(set(
        list(classesInModuleFromAll(module))
        +
        list(classesInModuleWithoutCheckingAll(module))
    ))


def onlyModels(userMadeModels):
    return [model for model in userMadeModels if models.Model in model.__mro__]


def isAbstract(clazz):
    try:
        return clazz.Meta.abstract
    except BaseException:
        return False


def discardAbstractModels(userMadeModels):
    return [model for model in userMadeModels if not isAbstract(model)]


def registrableModelsInModule(module):
    return discardAbstractModels(onlyModels(classesInModule(module)))


def registerForMe(admin, models_module):
    for model in registrableModelsInModule(models_module):
        try:
            admin.site.register(model)
        except exceptions.ImproperlyConfigured:
            pass
        except BaseException as e:
            print(f'{e.__class__.__name__}: {e}', file=stderr)
