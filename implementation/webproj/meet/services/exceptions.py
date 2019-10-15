# -*- encoding: utf-8 -*-

from django.http import Http404
from django.core.exceptions import PermissionDenied


class ServiceException(Exception):
    pass


class NotFoundException(Http404, ServiceException):
    pass


class NotAuthorizedException(PermissionDenied, ServiceException):
    pass


class FormValidationFailedException(ServiceException):
    pass


__all__ = [
    'ServiceException',
    'NotFoundException',
    'NotAuthorizedException',
    'FormValidationFailedException',
]
