import django.contrib.gis.admin
from django.contrib import admin
from ..adminModelRegister import register_for_me
from . import models

# Register your models here.

register_for_me(admin, models, models.User)
admin.site.unregister(models.Marker)
admin.site.unregister(models.Meet)
admin.site.register(models.Marker, django.contrib.gis.admin.OSMGeoAdmin)
admin.site.register(models.Meet, django.contrib.gis.admin.OSMGeoAdmin)
