# -*- encoding: utf-8 -*-

from pycdi.utils import Singleton
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from .. import models
from ..daos import PlaceSuggestionDAO
from .exceptions import NotAuthorizedException, FormValidationFailedException


@Singleton()
class MeetService:
    def delete_meet(self, user, meet):
        if user.pk == meet.creator.pk:
            meet.delete()
        else:
            raise NotAuthorizedException(_(
                'This data does not belong to the user who requested something about it.'
            ))

    def meet_delete_external_link(self, user, mel):
        if user.pk == mel.parent.creator.pk:
            mel.delete()
        else:
            raise NotAuthorizedException(_(
                'This data does not belong to the user who requested something about it.'
            ))

    def remove_star(self, user, star):
        if user.pk == star.owner.pk:
            star.delete()
        else:
            raise NotAuthorizedException(_(
                'This data does not belong to the user who requested something about it.'
            ))

    def add_update_meet(self, user, form):
        if not form.is_valid():
            raise FormValidationFailedException
        else:
            previous_one = models.Meet.objects.filter(
                id=form.cleaned_data.get('id', -1)
            ).first()
            if previous_one is not None and previous_one.creator.pk != user.pk:
                raise NotAuthorizedException(_(  # trying to update someone's else object
                    'This data does not belong to the user who requested something about it.'
                ))
            elif previous_one is None:  # new object
                current = form.save(commit=False)
                current.creator = user
                current.point = Point(form.cleaned_data['lat'], form.cleaned_data['lng'])
                current.save()
                return current
            else:  # update existing
                for k, v in form.cleaned_data.items():
                    setattr(previous_one, k, v)
                previous_one.point = Point(form.cleaned_data['lat'], form.cleaned_data['lng'])
                previous_one.save()
                return previous_one

    def meet_save_external_link(self, user, form, meet):
        if not form.is_valid():
            raise FormValidationFailedException
        else:
            previous_one = models.MeetExternalLinks.objects.filter(
                id=form.cleaned_data.get('id', -1)
            ).first()
            if previous_one is not None and previous_one.parent.creator.pk != user.pk:
                raise NotAuthorizedException(_(  # trying to update someone's else object
                    'This data does not belong to the user who requested something about it.'
                ))
            elif previous_one is None:  # new object
                current = form.save(commit=False)
                current.parent = meet
                current.save()
                return current
            else:  # update existing
                for k, v in form.cleaned_data.items():
                    setattr(previous_one, k, v)
                previous_one.save()
                return previous_one

    def add_update_star(self, user, form, meet):
        if not form.is_valid():
            raise FormValidationFailedException
        else:
            previous_one = models.MeetStar.objects.filter(
                id=form.cleaned_data.get('id', -1)
            ).first()
            if previous_one is not None and previous_one.owner.pk != user.pk:
                raise NotAuthorizedException(_(  # trying to update someone's else object
                    'This data does not belong to the user who requested something about it.'
                ))
            elif previous_one is None:  # new object
                current = form.save(commit=False)
                current.owner = user
                current.notified = False
                current.meet = meet
                current.save()
                return current
            else:  # update existing
                for k, v in form.cleaned_data.items():
                    setattr(previous_one, k, v)
                previous_one.save()
                return previous_one

    def meets_by_popularity(self, user):
        return self.all_listable_meets(user).annotate(s_count=Count('stars')).order_by('-s_count')

    def meets_by_distance(self, user, point):
        return self.all_listable_meets(user).filter(
            # Earth circumference: ~40 000km ; won't annotate without this useless filter
            point__distance_lte=(point, D(km=50000))
        ).annotate(distance=Distance("point", point)).order_by("distance")

    def meet_stars(self, user, meet):
        if meet in self.all_viewable_meets(user).all():
            return meet.stars.all()
        else:
            raise NotAuthorizedException(_(
                'User is not authorized to see this data.'
            ))
    
    def my_created_meets(self, user):
        return models.Meet.objects.filter(creator=user).all()

    def has_star(self, user, meet):
        if not user.is_authenticated:
            return None
        star = models.MeetStar.objects.filter(owner=user, meet=meet).first()
        if star is not None:
            return star
        else:
            return None

    def all_listable_meets(self, user):
        return self.all_viewable_meets(user).filter(privacy_unlisted=False).filter(meeting__gt=timezone.now())

    def all_viewable_meets(self, user):
        rs = models.Meet.objects
        if not user.is_authenticated:
            rs = rs.filter(privacy_require_account=False)
        return rs

    def assert_can_see_meet(self, user, meet):
        return meet in self.all_viewable_meets(user).all()

    def assert_can_edit_meet(self, user, meet):
        if meet.creator.pk != user.pk:
            raise NotAuthorizedException(_(
                'This data does not belong to the user who requested something about it.'
            ))

    def assert_can_edit_meet_external_link(self, user, mel):
        if mel.parent.creator.pk != user.pk:
            raise NotAuthorizedException(_(
                'This data does not belong to the user who requested something about it.'
            ))

    def meet_links(self, user, meet):
        self.assert_can_edit_meet(user, meet)
        return models.MeetExternalLinks.objects.filter(parent__pk=meet.pk).all()
    
    def send_star_emails_from_commandline(self):
        triggering_time = timezone.now()+timedelta(hours=6)
        stars_to_mail = models.MeetStar.objects.filter(meet__meeting__lte=triggering_time, notified=False).all()
        for star in stars_to_mail:
            context = dict(star=star, site=settings.ALLOWED_HOSTS[0])
            send_mail(
                subject=_('A meet you gave a star is about to start'),
                message=render_to_string('mail/star.txt', context=context),
                html_message=render_to_string('mail/star.html', context=context),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[star.owner.email],
                fail_silently=True
            )
            star.notified=True
            star.save()
    
    def place_suggestions(self, _, plchnt):
        return PlaceSuggestionDAO.get(plchnt)
