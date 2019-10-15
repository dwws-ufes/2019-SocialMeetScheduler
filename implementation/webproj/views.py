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


def ServerError(code):
    def handler(request, exc=None):
        return render(request, 'httperror.html', dict(error=code, exception=exc), status=code)
    return handler
