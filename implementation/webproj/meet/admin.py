import django.contrib.gis.admin
from django.contrib import admin
from ..adminModelRegister import registerForMe
from . import models

# Register your models here.

registerForMe(admin, models)
admin.site.unregister(models.Marker)
admin.site.unregister(models.Meet)
admin.site.register(models.Marker, django.contrib.gis.admin.OSMGeoAdmin)
admin.site.register(models.Meet, django.contrib.gis.admin.OSMGeoAdmin)
