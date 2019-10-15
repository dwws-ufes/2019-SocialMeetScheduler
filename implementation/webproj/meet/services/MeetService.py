# -*- encoding: utf-8 -*-

from pycdi.utils import Singleton
from django.db.models import Count
from django.utils import timezone
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from .. import models
from .exceptions import NotAuthorizedException, FormValidationFailedException


@Singleton()
class MeetService:
    def deleteMeet(self, user, meet):
        if user.pk == meet.creator.pk:
            meet.delete()
        else:
            raise NotAuthorizedException(_(
                'This data does not belong to the user who requested something about it.'
            ))

    def meetDeleteExternalLink(self, user, mel):
        if user.pk == mel.parent.creator.pk:
            mel.delete()
        else:
            raise NotAuthorizedException(_(
                'This data does not belong to the user who requested something about it.'
            ))

    def removeStar(self, user, star):
        if user.pk == star.owner.pk:
            star.delete()
        else:
            raise NotAuthorizedException(_(
                'This data does not belong to the user who requested something about it.'
            ))

    def addUpdateMeet(self, user, form):
        if not form.is_valid():
            raise FormValidationFailedException
        else:
            previousOne = models.Meet.objects.filter(
                id=form.cleaned_data.get('id', -1)
            ).first()
            if previousOne is not None and previousOne.creator.pk != user.pk:
                raise NotAuthorizedException(_(  # trying to update someone's else object
                    'This data does not belong to the user who requested something about it.'
                ))
            elif previousOne is None:  # new object
                current = form.save(commit=False)
                current.creator = user
                current.point = Point(form.cleaned_data['lat'], form.cleaned_data['lng'])
                current.save()
                return current
            else:  # update existing
                for k, v in form.cleaned_data.items():
                    setattr(previousOne, k, v)
                previousOne.point = Point(form.cleaned_data['lat'], form.cleaned_data['lng'])
                previousOne.save()
                return previousOne

    def meetSaveExternalLink(self, user, form, meet):
        if not form.is_valid():
            raise FormValidationFailedException
        else:
            previousOne = models.MeetExternalLinks.objects.filter(
                id=form.cleaned_data.get('id', -1)
            ).first()
            if previousOne is not None and previousOne.parent.creator.pk != user.pk:
                raise NotAuthorizedException(_(  # trying to update someone's else object
                    'This data does not belong to the user who requested something about it.'
                ))
            elif previousOne is None:  # new object
                current = form.save(commit=False)
                current.parent = meet
                current.save()
                return current
            else:  # update existing
                for k, v in form.cleaned_data.items():
                    setattr(previousOne, k, v)
                previousOne.save()
                return previousOne

    def addUpdateStar(self, user, form, meet):
        if not form.is_valid():
            raise FormValidationFailedException
        else:
            previousOne = models.MeetStar.objects.filter(
                id=form.cleaned_data.get('id', -1)
            ).first()
            if previousOne is not None and previousOne.owner.pk != user.pk:
                raise NotAuthorizedException(_(  # trying to update someone's else object
                    'This data does not belong to the user who requested something about it.'
                ))
            elif previousOne is None:  # new object
                current = form.save(commit=False)
                current.owner = user
                current.notified = False
                current.meet = meet
                current.save()
                return current
            else:  # update existing
                for k, v in form.cleaned_data.items():
                    setattr(previousOne, k, v)
                previousOne.save()
                return previousOne

    def meetsByPopularity(self, user):
        return self.allListableMeets(user).annotate(s_count=Count('stars')).order_by('-s_count')

    def meetsByDistance(self, user, point):
        return self.allListableMeets(user).filter(
            # Earth circumference: ~40 000km ; won't annotate without this useless filter
            point__distance_lte=(point, D(km=50000))
        ).annotate(distance=Distance("point", point)).order_by("distance")

    def meetStars(self, user, meet):
        if meet in self.allViewableMeets(user):
            return meet.stars.all()
        else:
            raise NotAuthorizedException(_(
                'User is not authorized to see this data.'
            ))

    def hasStar(self, user, meet):
        star = models.MeetStar.objects.filter(owner=user, meet=meet).first()
        if star is not None:
            return star.anonymous
        else:
            return None

    def allListableMeets(self, user):
        return self.allViewableMeets(user).filter(privacy_unlisted=False).filter(meeting__gt=timezone.now())

    def allViewableMeets(self, user):
        rs = models.Meet.objects
        if not user.is_authenticated:
            rs = rs.filter(privacy_require_account=False)
        return rs

    def assertCanSeeMeet(self, user, meet):
        return meet in self.allViewableMeets(user).all()

    def assertCanEditMeet(self, user, meet):
        if meet.creator.pk != user.pk:
            raise NotAuthorizedException(_(
                'This data does not belong to the user who requested something about it.'
            ))

    def assertCanEditMeetExternalLink(self, user, mel):
        if mel.parent.creator.pk != user.pk:
            raise NotAuthorizedException(_(
                'This data does not belong to the user who requested something about it.'
            ))

    def meetLinks(self, user, meet):
        self.assertCanEditMeet(user, meet)
        return models.MeetExternalLinks.objects.filter(parent__pk=meet.pk).all()
