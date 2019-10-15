# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.gis.db import models as gismodels
from .Marker import Marker, User


class Meet(Marker):
    title = models.CharField(
        blank=False,
        null=False,
        max_length=100,
        primary_key=False
    )

    description = models.TextField(
        blank=False,
        null=False,
        primary_key=False
    )

    meeting = models.DateTimeField(
        blank=False,
        null=False,
        primary_key=False
    )

    # stars: MeetStar

    # chats: Set[ChatMailbox]

    # external_links: Set[MeetExternalLinks]
