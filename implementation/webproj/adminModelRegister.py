from django.db import models
from .stackOverflowSnippets import classesInModule
from django.core import exceptions
from sys import stderr


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
            print(str(e.__class__)+': '+str(e), file=stderr)
