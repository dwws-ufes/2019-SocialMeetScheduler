# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.gis.db import models as gismodels


class ChatMailbox(models.Model):
    last_sent = models.DateTimeField(
        blank=False,
        null=False,
        primary_key=False
    )

    # chatmessage: Set[ChatMessage]

    user = models.ForeignKey(
        "User",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="chatmailbox"
    )

    meet = models.ForeignKey(
        "Meet",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="chatmailbox"
    )

    user = models.ForeignKey(
        "User",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="chatmailbox"
    )
