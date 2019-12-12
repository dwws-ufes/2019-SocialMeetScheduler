# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.auth import get_user_model
from .ChatMailbox import ChatMailbox

User = get_user_model()


class ChatMessage(models.Model):
    message = models.TextField(
        blank=False,
        null=False,
        primary_key=False
    )

    sent = models.DateTimeField(
        blank=False,
        null=False,
        primary_key=False
    )

    read = models.BooleanField(
        blank=False,
        null=False,
        primary_key=False
    )

    chatmailbox = models.ForeignKey(
        ChatMailbox,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="chatmessage"
    )

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="chatmessage"
    )
