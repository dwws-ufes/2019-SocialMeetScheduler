# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.gis import forms as gisforms
from django.utils.translation import ugettext_lazy as _
from leaflet.forms.widgets import LeafletWidget

from .. import formMetaTools
from . import models


class MeetForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    lat = forms.FloatField(widget=forms.HiddenInput())
    lng = forms.FloatField(widget=forms.HiddenInput())

    class Meta(metaclass=formMetaTools.ModelFormMetaMetaclass):
        model = models.Meet
        fields = [
            'id',
            'title',
            'description',
            'meeting',
            'name',
            # 'point',
            'privacy_require_account',
            'privacy_unlisted',
        ]
        widgets = {
            'id': forms.HiddenInput(),
            # 'point': gisforms.OSMWidget(),
            'meeting': forms.DateTimeInput(),
        }


class ConversationForm(forms.ModelForm):
    class Meta(metaclass=formMetaTools.ModelFormMetaMetaclass):
        model = models.ChatMessage
        fields = [
            'message',
        ]


class MeetExternalLinksForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta(metaclass=formMetaTools.ModelFormMetaMetaclass):
        model = models.MeetExternalLinks
        fields = [
            'id',
            'name',
            'url',
        ]
        widgets = {'id': forms.HiddenInput()}


class MeetStarForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta(metaclass=formMetaTools.ModelFormMetaMetaclass):
        model = models.MeetStar
        fields = [
            'id',
            'anonymous',
        ]
        widgets = {'id': forms.HiddenInput(), 'anonymous': forms.HiddenInput()}
