# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.auth import get_user_model
from uuid import uuid4

User = get_user_model()


class Marker(models.Model):
    key = models.UUIDField(
        blank=False,
        null=False,
        primary_key=False,
        unique=True,
        default=uuid4
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
        primary_key=False,
        srid=4326
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
        primary_key=False,
        auto_now_add=True
    )

    last_modified = models.DateTimeField(
        blank=False,
        null=False,
        primary_key=False,
        auto_now=True
    )

    creator = models.ForeignKey(
        User,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="markers"
    )
