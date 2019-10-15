# -*- encoding: utf-8 -*-

from django.views.generic.base import TemplateView
from django.views.generic.base import View
from django.db.models import Model as BaseModel
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import Http404
from django.core.exceptions import PermissionDenied as Http403
from typing import Union
from typing import Any
from typing import List
from typing import Dict
from pycdi import Inject
import page_components

from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _

from ..modelSolverServiceOnView import ModelSolver
from ..kwargsRenamer import KeywordArgumentsRenamer

from . import services
from . import forms
from . import models

# Create your controllers here.


class Placeholder(TemplateView):
    template_name = 'soon.html'


class ControllableMixin(object):
    template_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_validate()

    def _init_validate(self):
        if type(self).template_name is None:
            raise NotImplementedError(
                "Class attribute template_name must "
                "be overriden on child controller."
            )
        return True


class UpsertMixin(ControllableMixin):
    SRVC_UPS_METHOD = None

    def _init_validate(self):
        if type(self).SRVC_UPS_METHOD is None:
            raise NotImplementedError(
                "Class attribute SRVC_UPS_METHOD must "
                "be overriden on child controller."
            )
        return super()._init_validate()

    def post(self, request: HttpRequest, service, form: forms.forms.Form, **kwargs: Dict[str, Any]) -> HttpResponse:
        return getattr(service, type(self).SRVC_UPS_METHOD)(request.user, form, **kwargs)


class DeleteMixin(ControllableMixin):
    SRVC_DEL_METHOD = None

    def _init_validate(self):
        if type(self).SRVC_DEL_METHOD is None:
            raise NotImplementedError(
                "Class attribute SRVC_DEL_METHOD must "
                "be overriden on child controller."
            )
        return super()._init_validate()

    def delete(self, request: HttpRequest, service, model: BaseModel, **kwargs: Dict[str, Any]) -> HttpResponse:
        return getattr(service, type(self).SRVC_DEL_METHOD)(request.user, model, **kwargs)


class DetailsMixin(ControllableMixin):
    SRVC_DTL_METHOD = None

    def _init_validate(self):
        if type(self).SRVC_DTL_METHOD is None:
            raise NotImplementedError(
                "Class attribute SRVC_DTL_METHOD must "
                "be overriden on child controller."
            )
        return super()._init_validate()

    def get(self, request: HttpRequest, service, model: BaseModel, **kwargs: Dict[str, Any]) -> HttpResponse:
        return getattr(service, type(self).SRVC_DTL_METHOD)(request.user, model, **kwargs)


class ListMixin(ControllableMixin):
    SRVC_LST_METHOD = None

    def _init_validate(self):
        if type(self).SRVC_LST_METHOD is None:
            raise NotImplementedError(
                "Class attribute SRVC_LST_METHOD must "
                "be overriden on child controller."
            )
        return super()._init_validate()

    def get(self, request: HttpRequest, service, **kwargs: Dict[str, Any]) -> HttpResponse:
        return getattr(service, type(self).SRVC_LST_METHOD)(request.user, **kwargs)

##########################################################
#### REAL STUFF BEGINS HERE ##############################
##########################################################


class AddRemoveFriendButton(page_components.TemplatePageComponent):
    template_name = 'togglefriendbutton.html'

    @classmethod
    def from_service(cls, request: HttpRequest, service: services.FriendService, current_user: models.User, friendable: models.User) -> 'AddRemoveFriendButton':
        is_friend = service.isFriendOf(current_user, friendable)
        is_pending = service.isFriendshipWithPending(current_user, friendable)
        return cls(request, friendable, is_friend, is_pending)

    def __init__(self, request: HttpRequest, friendable: models.User, is_friend: bool, is_pending: bool):
        self.friendable = friendable
        self.is_friend = is_friend
        self.is_pending = is_pending
        self.rq = request

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{'friendable': self.friendable, 'is_friend': self.is_friend, 'is_pending': self.is_pending, **kwargs})

    def render(self):
        template_name = self.get_template_name()
        context_data = self.get_context_data()
        return mark_safe(render(self.rq, template_name, context=context_data).content.decode())


@method_decorator(login_required, name='dispatch')
class MyAccount(TemplateView):
    template_name = 'myaccount.html'

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(*args, **kwargs)


@method_decorator(login_required, name='post')
@method_decorator(login_required, name='delete')
@method_decorator(ModelSolver(username=models.User, to_raise=Http404(_('usr_not_found'))), name='dispatch')
@method_decorator(KeywordArgumentsRenamer(username='user'), name='dispatch')
@method_decorator(Inject(service=services.FriendService), name='dispatch')
class Friendship(View):
    def get(self, request: HttpRequest, service: services.FriendService, user: models.User) -> HttpResponse:
        return render(request, 'user.html', {
            'friend': user,
            'button': AddRemoveFriendButton.from_service(request, service, request.user, user),
            'form': forms.ConversationForm() if service.isFriendOf(request.user, user) else None
        })

    def post(self, request: HttpRequest, service: services.FriendService, user: models.User) -> HttpResponse:
        service.startFriendshipWith(request.user, user)
        return redirect('user', username=user.username)

    def delete(self, request: HttpRequest, service: services.FriendService, user: models.User) -> HttpResponse:
        service.breakFriendshipWith(request.user, user)
        return redirect('user', username=user.username)


@method_decorator(login_required, name='dispatch')
@method_decorator(Inject(service=services.FriendService), name='dispatch')
class Friends(View, ListMixin):
    SRVC_LST_METHOD = 'friends'

    def get(self, request: HttpRequest, service: services.FriendService) -> HttpResponse:
        friends = super().get(request, service)
        return render(request, 'friends.html', {
            'friends': [{
                'item': friend,
                'button': AddRemoveFriendButton.from_service(request, service, request.user, friend),
            } for friend in friends]
        })


@method_decorator(login_required, name='dispatch')
@method_decorator(Inject(service=services.MessengerService), name='dispatch')
class Conversations(View, ListMixin):
    SRVC_LST_METHOD = 'listMailboxes'

    def get(self, request: HttpRequest, service: services.MessengerService) -> HttpResponse:
        mailboxes = super().get(request, service)
        return render(request, 'mailboxes.html', {
            'mailboxes': mailboxes,
        })


@method_decorator(login_required, name='dispatch')
@method_decorator(ModelSolver(pk=models.ChatMailbox, to_raise=Http404(_('cht_not_found'))), name='dispatch')
@method_decorator(KeywordArgumentsRenamer(pk='mailbox'), name='dispatch')
@method_decorator(Inject(service=services.MessengerService), name='dispatch')
class Conversation(View, ListMixin, UpsertMixin):
    SRVC_LST_METHOD = 'readMailbox'
    SRVC_UPS_METHOD = 'sendMessage'

    def get(self, request: HttpRequest, service: services.MessengerService, mailbox: models.ChatMailbox) -> HttpResponse:
        super().get(request, service, mailbox=mailbox)
        form = forms.ConversationForm()
        return render(request, 'mailbox_messages.html', {
            'mailbox': mailbox,
            'form': form,
        })

    def post(self, request: HttpRequest, service: services.MessengerService, mailbox: models.ChatMailbox) -> HttpResponse:
        form = forms.ConversationForm(request.POST)
        try:
            super().post(request, service, form, mailbox=mailbox)
        except services.FormValidationFailedException:
            return render(request, 'mailbox_messages.html', {
                'mailbox': mailbox,
                'form': form,
            })
        return redirect('conversation', pk=mailbox.pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(ModelSolver(username=models.User, to_raise=Http404(_('usr_not_found'))), name='dispatch')
@method_decorator(KeywordArgumentsRenamer(username='user'), name='dispatch')
@method_decorator(Inject(service1=services.FriendService, service2=services.MessengerService), name='dispatch')
class TalkToFriend(View, DetailsMixin, UpsertMixin):
    SRVC_DTL_METHOD = 'assertIsFriend'
    SRVC_UPS_METHOD = 'sendMessageToFriend'

    def get(self, request: HttpRequest, service1: services.FriendService, user: models.User, service2) -> HttpResponse:
        service = service1
        super().get(request, service, user)
        form = forms.ConversationForm()
        return render(request, 'talktofriend.html', {
            'form': form,
            'friend': user,
        })

    def post(self, request: HttpRequest, service2: services.MessengerService, user: models.User, service1) -> HttpResponse:
        service = service2
        form = forms.ConversationForm(request.POST)
        message = None
        try:
            message = super().post(request, service, form, friend=user)
        except services.FormValidationFailedException:
            return render(request, 'talktofriend.html', {
                'form': form,
                'friend': user,
            })
        return redirect('conversation', pk=message.mailbox.pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(ModelSolver(key=models.Meet, to_raise=Http404(_('meet_not_found'))), name='dispatch')
@method_decorator(KeywordArgumentsRenamer(key='meet'), name='dispatch')
@method_decorator(Inject(service1=services.MeetService, service2=services.MessengerService), name='dispatch')
class TalkToMeetOrganizer(View, DetailsMixin, UpsertMixin):
    SRVC_DTL_METHOD = 'assertCanSeeMeet'
    SRVC_UPS_METHOD = 'sendMessageToMeetOrganizer'

    def get(self, request: HttpRequest, service1: services.MeetService, meet: models.Meet, service2) -> HttpResponse:
        service = service1
        super().get(request, service, meet)
        form = forms.ConversationForm()
        return render(request, 'talktomeetorganizer.html', {
            'form': form,
            'meet': meet,
        })

    def post(self, request: HttpRequest, service2: services.MessengerService, meet: models.Meet, service1) -> HttpResponse:
        service = service2
        form = forms.ConversationForm(request.POST)
        message = None
        try:
            message = super().post(request, service, form, meet=meet)
        except services.FormValidationFailedException:
            return render(request, 'talktomeetorganizer.html', {
                'form': form,
                'meet': meet,
            })
        return redirect('conversation', pk=message.mailbox.pk)


@method_decorator(Inject(service=services.MeetService), name='dispatch')
class MeetsPopular(View, ListMixin):
    SRVC_LST_METHOD = 'meetsByPopularity'

    def get(self, request: HttpRequest, service: services.MeetService):
        meets = super().get(request, service)
        return render(request, 'meets.html', {
            'meets': meets,
            'by': 'popularity',
        })


@method_decorator(Inject(service=services.MeetService), name='dispatch')
class MeetsNearby(View, ListMixin):
    SRVC_LST_METHOD = 'meetsByDistance'

    def get(self, request: HttpRequest, service: services.MeetService, lats: str = None, longs: str = None):
        reference_point = None
        try:
            longf = float(longs)
            latf = float(lats)
            reference_point = Point(longf, latf)
        except BaseException:
            if 'lat' in request.GET and 'long' in request.GET:
                return redirect('meets_nearby_precise', lats=request.GET['lat'], longs=request.GET['long'])
            else:
                pass
        if reference_point is None:
            return render(request, 'asklatlong.html', {'next': request.path})
        else:
            meets = super().get(request, service, point=reference_point)
            return render(request, 'meets.html', {
                'meets': meets,
                'by': 'distance',
            })


@method_decorator(ModelSolver(key=models.Meet, to_raise=Http404(_('meet_not_found'))), name='dispatch')
@method_decorator(KeywordArgumentsRenamer(key='meet'), name='dispatch')
@method_decorator(Inject(service=services.MeetService), name='dispatch')
class MeetView(View, DetailsMixin):
    SRVC_DTL_METHOD = 'assertCanSeeMeet'

    def get(self, request: HttpRequest, service: services.MeetService, meet: models.Meet):
        super().get(request, service, meet)
        return render(request, 'meet_view.html', {
            'meet': meet,
        })


@method_decorator(login_required, name='dispatch')
@method_decorator(Inject(service=services.MeetService), name='dispatch')
class MeetNew(View, UpsertMixin):
    SRVC_UPS_METHOD = 'addUpdateMeet'

    def get(self, request: HttpRequest, service: services.MeetService):
        return render(request, 'meet_edit.html', {
            'form': forms.MeetForm(),
        })

    def post(self, request: HttpRequest, service: services.MeetService):
        form = forms.MeetForm(request.POST)
        meet = None
        try:
            meet = super().post(request, service, form)
        except services.FormValidationFailedException:
            return render(request, 'meet_edit.html', {
                'form': form,
            })
        return redirect('meet', key=meet.key)


@method_decorator(ModelSolver(key=models.Meet, to_raise=Http404(_('meet_not_found'))), name='dispatch')
@method_decorator(KeywordArgumentsRenamer(key='meet'), name='dispatch')
@method_decorator(login_required, name='dispatch')
@method_decorator(Inject(service=services.MeetService), name='dispatch')
class MeetEdit(View, DetailsMixin, UpsertMixin, DeleteMixin):
    SRVC_DTL_METHOD = 'assertCanEditMeet'
    SRVC_UPS_METHOD = 'addUpdateMeet'
    SRVC_DEL_METHOD = 'deleteMeet'

    def get(self, request: HttpRequest, service: services.MeetService, meet: models.Meet):
        super().get(request, service, meet)
        form = forms.MeetForm(instance=meet)
        form.data['lat'] = meet.point.y
        form.data['lng'] = meet.point.x
        return render(request, 'meet_edit.html', {
            'form': form,
        })

    def post(self, request: HttpRequest, service: services.MeetService, meet: models.Meet):
        form = forms.MeetForm(request.POST)
        try:
            super().post(request, service, form)
        except services.FormValidationFailedException:
            return render(request, 'meet_edit.html', {
                'form': form,
            })
        return redirect('meet', key=meet.key)

    def delete(self, request: HttpRequest, service: services.MeetService, meet: models.Meet):
        meet = super().delete(request, service, meet)
        return redirect('index')


@method_decorator(ModelSolver(key=models.Meet, to_raise=Http404(_('meet_not_found'))), name='dispatch')
@method_decorator(KeywordArgumentsRenamer(key='meet'), name='dispatch')
@method_decorator(login_required, name='dispatch')
@method_decorator(Inject(service=services.MeetService), name='dispatch')
class MeetLinksEdit(View, ListMixin, UpsertMixin):
    SRVC_LST_METHOD = 'meetLinks'
    SRVC_UPS_METHOD = 'meetSaveExternalLink'

    def get(self, request: HttpRequest, service: services.MeetService, meet: models.Meet):
        mels = super().get(request, service, meet=meet)
        return render(request, 'meet_external_links_edit.html', {
            'mels': mels,
            'form': forms.MeetExternalLinksForm(),
        })

    def post(self, request: HttpRequest, service: services.MeetService, meet: models.Meet):
        form = forms.MeetExternalLinksForm(request.POST)
        try:
            super().post(request, service, form, meet=meet)
        except services.FormValidationFailedException:
            return render(request, 'meet_external_links_edit.html', {
                'form': form,
            })
        return redirect('meetlinks', key=meet.key)


@method_decorator(ModelSolver(pk=models.MeetExternalLinks, to_raise=Http404(_('meet_not_found'))), name='dispatch')
@method_decorator(KeywordArgumentsRenamer(pk='mel'), name='dispatch')
@method_decorator(login_required, name='dispatch')
@method_decorator(Inject(service=services.MeetService), name='dispatch')
class MeetLinkEdit(View, DetailsMixin, UpsertMixin, DeleteMixin):
    SRVC_DTL_METHOD = 'assertCanEditMeetExternalLink'
    SRVC_UPS_METHOD = 'meetSaveExternalLink'
    SRVC_DEL_METHOD = 'meetDeleteExternalLink'

    def get(self, request: HttpRequest, service: services.MeetService, mel: models.MeetExternalLinks):
        super().get(request, service, mel)
        return render(request, 'meet_external_links_edit.html', {
            'mel': mel,
            'form': forms.MeetExternalLinksForm(instance=mel),
        })

    def post(self, request: HttpRequest, service: services.MeetService, mel: models.MeetExternalLinks):
        form = forms.MeetExternalLinksForm(request.POST)
        try:
            super().post(request, service, form, meet=mel.parent)
        except services.FormValidationFailedException:
            return render(request, 'meet_external_links_edit.html', {
                'mel': mel,
                'form': form,
            })
        return redirect('meetlinks', key=mel.parent.key)

    def delete(self, request: HttpRequest, service: services.MeetService, mel: models.MeetExternalLinks):
        super().delete(request, service, mel)
        return redirect('meetlinks', key=mel.parent.key)


class MeetStarButton(page_components.TemplatePageComponent):
    template_name = 'meetstarbutton.html'

    def __init__(self, meet, hasStar):
        self.meet = meet
        self.hasStar = hasStar

    def get_context_data(self, **kwargs):
        return super().get_context_data(**dict(
            meet=self.meet,
            hasStar=self.hasStar,
            anonymousForm=forms.MeetStarForm(dict(anonymous=True)),
            publicForm=forms.MeetStarForm(dict(anonymous=False))
        ), **kwargs)


@method_decorator(ModelSolver(key=models.Meet, to_raise=Http404(_('meet_not_found'))), name='dispatch')
@method_decorator(KeywordArgumentsRenamer(key='meet'), name='dispatch')
@method_decorator(Inject(service=services.MeetService), name='dispatch')
class MeetStars(View, ListMixin, UpsertMixin):
    SRVC_LST_METHOD = 'meetStars'
    SRVC_UPS_METHOD = 'addUpdateStar'

    def get(self, request: HttpRequest, service: services.MeetService, meet: models.Meet):
        stars = super().get(request, service)
        return render(request, 'meetstars.html', {
            'meet': meet,
            'stars': stars,
            'button': MeetStarButton(meet, service.hasStar(request.user, meet)),
        })

    def post(self, request: HttpRequest, service: services.MeetService, meet: models.Meet):
        form = forms.MeetStarForm(request.POST)
        try:
            super().post(request, service, form, meet=meet)
        except services.FormValidationFailedException:
            stars = super().get(request, service)
            return render(request, 'meetstars.html', {
                'meet': meet,
                'stars': stars,
                'button': MeetStarButton(meet, service.hasStar(request.user, meet)),
            })
        return redirect('meetstars', key=meet.key)


@method_decorator(ModelSolver(pk=models.MeetStar, to_raise=Http404(_('meetstar_not_found'))), name='dispatch')
@method_decorator(KeywordArgumentsRenamer(pk='meetStar'), name='dispatch')
@method_decorator(login_required, name='dispatch')
@method_decorator(Inject(service=services.MeetService), name='dispatch')
class MeetStarEdit(View, DeleteMixin):
    SRVC_DEL_METHOD = 'removeStar'

    def delete(self, request: HttpRequest, service: services.MeetService, meetStar: models.MeetStar):
        super().delete(request, service, meetStar)
        return redirect('meetstars', key=meetStar.meet.key)
