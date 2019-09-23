# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.gis.db import models as gismodels


class Marker():
    key = models.UUIDField(
        blank=False,
        null=False,
        primary_key=False
    )

    name = models.CharField(
        blank=False,
        null=False,
        max_length=75,
        primary_key=False
    )

    point = gismodels.PointField(
        blank=False,
        null=False,
        primary_key=False
    )

    privacy_require_account = models.BooleanField(
        blank=False,
        null=False,
        primary_key=False
    )

    privacy_unlisted = models.BooleanField(
        blank=False,
        null=False,
        primary_key=False
    )

    created = models.DateTimeField(
        blank=False,
        null=False,
        primary_key=False
    )

    last_modified = models.DateTimeField(
        blank=False,
        null=False,
        primary_key=False
    )

    user = models.OneToOneField(
        "User",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="marker"
    )
