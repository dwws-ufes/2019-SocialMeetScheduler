# -*- encoding: utf-8 -*-

from django import template
from django.db.models import Model
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from ..services import LDService

register = template.Library()

@register.filter(is_safe=True)
def linkeddata(model, fmt='rdf'):
    if model is not None and isinstance(model, Model) and hasattr(model, 'id'):
        lds: LDService = LDService()
        uri = str(lds.uri_of(model))
        mime = LDService.serializers[fmt if fmt in LDService.serializers else 'rdf'][1]
        return mark_safe(render_to_string('linkeddata.head.html', {'uri': uri, 'mime': mime}))
    else:
        return mark_safe("")
