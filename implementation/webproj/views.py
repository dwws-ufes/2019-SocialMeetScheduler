# -*- encoding: utf-8 -*-

from django.shortcuts import redirect, render
from django.views.generic.base import View
import pytz


class TimezoneSetter(View):
    def get(self, request):
        return render(request, 'tz.html', {
            'timezones': pytz.common_timezones,
            'next': request.GET.get('next', '/')
        })

    def post(self, request):
        request.session['django_timezone'] = request.POST['timezone']
        return redirect(request.GET.get('next', '/'))


class ServerError(object):
    def __init__(self, code):
        self._code = code

    def __call__(self, request, exception=None):
        return render(
            request,
            'httperror.html',
            dict(
                error=self._code,
                exception=exception
            ),
            status=self._code
        )
