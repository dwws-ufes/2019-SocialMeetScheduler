# -*- encoding: utf-8 -*-

from pycdi.utils import Singleton
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from .exceptions import NotAuthorizedException
from .. import models


@Singleton()
class FriendService:
    def startFriendshipWith(self, user, friend):
        if user == friend:
            raise NotAuthorizedException(_(
                'You cannot friend yourself.'
            ))
        else:
            friendship = self._potential_friendships(user, friend).first()
            if friendship is None:
                friendship = models.Friendship()
                friendship.is_request = True
                friendship.initiator = user
                friendship.initiated = friend
                friendship.save()
            elif friendship.initiator == friend:
                if friendship.is_request:
                    friendship.is_request = False
                    friendship.save()
                else:
                    pass # Friendship exists and was already accepted
            else:
                pass  # Friendship request exists as is

    def breakFriendshipWith(self, user, friend):
        self._potential_friendships(user, friend).delete()

    def isFriendshipWithPending(self, user, friend):
        friendship = self._potential_friendships(user, friend).first()
        return friendship is not None and friendship.is_request

    def isFriendOf(self, user, friend):
        return self._potential_friendships(user, friend).filter(is_request=False).exists()

    def assertIsFriend(self, user, friend):
        if not self.isFriendOf(user, friend):
            raise NotAuthorizedException(_(
                'This action is not possible if both users are not friends.'
            ))

    def friends(self, user):
        return models.Friendship.objects.filter(
            Q(initiator=user) | Q(initiated=user)
        ).order_by('-is_request').all()

    def _potential_friendships(self, user, friend):
        return models.Friendship.objects.filter(
            Q(
                initiator=user,
                initiated=friend
            ) | Q(
                initiator=friend,
                initiated=user
            )
        )
