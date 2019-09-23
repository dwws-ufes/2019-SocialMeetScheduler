# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.gis.db import models as gismodels
from .Meet import Meet


class MeetExternalLinks(models.Model):
    name = models.CharField(
        blank=False,
        null=False,
        max_length=75,
        primary_key=False
    )

    url = models.URLField(
        blank=False,
        null=False,
        primary_key=False
    )

    meet = models.ForeignKey(
        Meet,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="meetexternallinks"
    )
