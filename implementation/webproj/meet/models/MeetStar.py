# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.auth import get_user_model
from .Meet import Meet

User = get_user_model()


class MeetStar(models.Model):
    anonymous = models.BooleanField(
        blank=False,
        null=False,
        primary_key=False
    )

    last_modified = models.DateTimeField(
        blank=False,
        null=False,
        primary_key=False
    )

    notified = models.BooleanField(
        blank=False,
        null=False,
        primary_key=False
    )

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="meetstar"
    )

    meet = models.ForeignKey(
        Meet,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="meetstar"
    )
