# -*- encoding: utf-8 -*-

from pycdi.utils import Singleton
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from .exceptions import NotAuthorizedException
from .. import models


@Singleton()
class FriendService:
    def start_friendship_with(self, user, friend):
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

    def break_friendship_with(self, user, friend):
        self._potential_friendships(user, friend).delete()

    def is_friendship_with_pending(self, user, friend):
        friendship = self._potential_friendships(user, friend).first()
        return friendship is not None and friendship.is_request

    def is_initiator_of_friendship(self, user, friend):
        friendship = self._potential_friendships(user, friend).first()
        return friendship is not None and (friendship.initiator.pk == user.pk)

    def is_friend_of(self, user, friend):
        return self._potential_friendships(user, friend).filter(is_request=False).exists()

    def assert_is_friend(self, user, friend):
        if not self.is_friend_of(user, friend):
            raise NotAuthorizedException(_(
                'This action is not possible if both users are not friends.'
            ))

    def friends(self, user):
        return models.Friendship.objects.filter(
            Q(initiator=user) | Q(initiated=user)
        ).order_by('-is_request').all()

    def established_friends(self, user):
        return models.Friendship.objects.filter(
            Q(initiator=user) | Q(initiated=user)
        ).filter(is_request=False).all()

    def _potential_friendships(self, user, friend):
        if user.is_anonymous:
            return models.Friendship.objects.filter(
                initiator=None,
                initiated=None
            )
        return models.Friendship.objects.filter(
            Q(
                initiator=user,
                initiated=friend
            ) | Q(
                initiator=friend,
                initiated=user
            )
        )
