# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.auth import get_user_model

User = get_user_model()


class Friendship(models.Model):
    is_request = models.BooleanField(
        blank=False,
        null=False,
        primary_key=False
    )

    since = models.DateTimeField(
        blank=False,
        null=False,
        primary_key=False
    )

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="friendship"
    )

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="friendship"
    )
