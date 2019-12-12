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
        primary_key=False,
        auto_now_add=True
    )

    read = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        primary_key=False
    )

    mailbox = models.ForeignKey(
        ChatMailbox,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        User,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="messages"
    )
