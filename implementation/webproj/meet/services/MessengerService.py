# -*- encoding: utf-8 -*-

from pycdi.utils import Singleton
from pycdi import Inject
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .FriendService import FriendService
from .MeetService import MeetService
from .exceptions import FormValidationFailedException
from .exceptions import NotAuthorizedException
from .. import models


@Singleton()
class MessengerService:
    def __init__(self):
        self.friend_service = FriendService()
        self.meet_service = MeetService()

    def send_message(self, user, form, mailbox):
        self.assert_mailbox_readable(user, mailbox)
        if not form.is_valid():
            raise FormValidationFailedException
        else:
            message = models.ChatMessage()
            message.message = form.cleaned_data['message']
            message.read = False
            message.mailbox = mailbox
            message.sender = user
            message.save()
            mailbox.save()
            recipient = mailbox.initiated if mailbox.initiator.pk==user.pk else mailbox.initiator
            context = dict(
                message=message.message,
                site=settings.ALLOWED_HOSTS[0],
                recipient=recipient,
                sender=user,
                mailbox=mailbox
            )
            send_mail(
                subject=_('Someone has sent you a private message'),
                message=render_to_string('mail/message.txt', context=context),
                html_message=render_to_string('mail/message.html', context=context),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=True
            )
            return message

    def send_message_to_friend(self, user, form, friend):
        if not form.is_valid():
            raise FormValidationFailedException
        else:
            self.friend_service.assert_is_friend(user, friend)
            mailbox = models.ChatMailbox.objects.filter(
                Q(initiator=user, initiated=friend, meet=None) |
                Q(initiator=friend, initiated=user, meet=None)
            ).first()
            if mailbox is None:
                mailbox = models.ChatMailbox()
                mailbox.initiator = user
                mailbox.initiated = friend
                mailbox.meet = None
                mailbox.save()
            return self.send_message(user, form, mailbox)

    def send_message_to_meet_organizer(self, user, form, meet):
        if not form.is_valid():
            raise FormValidationFailedException
        else:
            self.meet_service.assert_can_see_meet(user, meet)
            mailbox = models.ChatMailbox.objects.filter(
                Q(initiator=user, initiated=meet.creator, meet=meet)
            ).first()
            if mailbox is None:
                mailbox = models.ChatMailbox()
                mailbox.initiator = user
                mailbox.initiated = meet.creator
                mailbox.meet = meet
                mailbox.save()
            return self.send_message(user, form, mailbox)

    def list_mailboxes(self, user):
        if user.is_anonymous:
            return models.ChatMailbox.objects.filter(initiator=None, initiated=None).all()
        return models.ChatMailbox.objects.filter(Q(initiator=user) | Q(initiated=user)).all()

    def read_mailbox(self, user, mailbox, quietly=False):
        self.assert_mailbox_readable(user, mailbox)
        other = mailbox.initiator
        if other.pk == user.pk:
            other = mailbox.initiated
        if not quietly:
            mailbox.messages.filter(sender=other, read=False).update(read=True)
        return mailbox.messages.all()

    def assert_mailbox_readable(self, user, mailbox):
        if mailbox.initiator.pk != user.pk and mailbox.initiated.pk != user.pk:
            raise NotAuthorizedException(_(  # trying to update someone's else object
                'This data does not belong to the user who requested something about it.'
            ))
