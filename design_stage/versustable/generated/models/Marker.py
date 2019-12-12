# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.auth import get_user_model

User = get_user_model()


class Marker(models.Model):
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

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="marker"
    )

    last_modified = models.URLField(
        blank=False,
        null=False,
        primary_key=False
    )
