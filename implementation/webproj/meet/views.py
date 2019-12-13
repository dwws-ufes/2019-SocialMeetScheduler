# -*- encoding: utf-8 -*-

from django.views.generic.base import TemplateView
from django.views.generic.base import View
from django.db.models import Model as BaseModel
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
from django.utils.html import urlencode
from django.shortcuts import resolve_url
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import Http404
from django.core.exceptions import PermissionDenied as Http403
from typing import Union
from typing import Any
from typing import List
from typing import Dict
from pycdi import Inject
import page_components
import requests

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


class TemplatePageComponentFixed(page_components.TemplatePageComponent):
    def __init__(self, request: HttpRequest):
        self._request = request
    
    def render(self):
        return mark_safe(render(
            self._request,
            self.get_template_name(),
            context=self.get_context_data()
        ).content.decode())


##########################################################
#### REAL STUFF BEGINS HERE ##############################
##########################################################


class AddRemoveFriendButton(TemplatePageComponentFixed):
    template_name = 'togglefriendbutton.html'

    @classmethod
    def from_service(cls, request: HttpRequest, service: services.FriendService, current_user: models.User, friendable: models.User) -> 'AddRemoveFriendButton':
        is_friend = service.is_friend_of(current_user, friendable)
        is_pending = service.is_friendship_with_pending(current_user, friendable)
        is_initiator = service.is_initiator_of_friendship(current_user, friendable)
        return cls(request, friendable, is_friend, is_pending, is_initiator)

    def __init__(self, request: HttpRequest, friendable: models.User, is_friend: bool, is_pending: bool, is_initiator: bool):
        super().__init__(request)
        self.friendable = friendable
        self.is_friend = is_friend
        self.is_pending = is_pending
        self.is_initiator = is_initiator

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{
            'friendable': self.friendable,
            'is_friend': self.is_friend,
            'is_pending': self.is_pending,
            'is_initiator': self.is_initiator,
            **kwargs
        })



@method_decorator(login_required, name='dispatch')
@method_decorator(Inject(meet_service=services.MeetService), name='dispatch')
class MyAccount(TemplateView):
    template_name = 'myaccount.html'

    def get(self, request: HttpRequest, meet_service: services.MeetService):
        return render(request, self.get_template_names(), {
            'userMeets': meet_service.my_created_meets(request.user)
        })


@method_decorator(login_required, name='post')
@method_decorator(login_required, name='delete')
@method_decorator(ModelSolver(username=models.User, to_raise=Http404(_('usr_not_found'))), name='dispatch')
@method_decorator(KeywordArgumentsRenamer(username='user'), name='dispatch')
@method_decorator(Inject(service=services.FriendService), name='dispatch')
class Friendship(View):
    def get(self, request: HttpRequest, service: services.FriendService, user: models.User) -> HttpResponse:
        return render(request, 'user.html', {
            'friend': user,
            'friends': service.established_friends(user),
            'button': AddRemoveFriendButton.from_service(request, service, request.user, user),
            'form': forms.ConversationForm() if service.is_friend_of(request.user, user) else None
        })

    def post(self, request: HttpRequest, service: services.FriendService, user: models.User) -> HttpResponse:
        service.start_friendship_with(request.user, user)
        return redirect('user', username=user.username)

    def delete(self, request: HttpRequest, service: services.FriendService, user: models.User) -> HttpResponse:
        service.break_friendship_with(request.user, user)
        return redirect('user', username=user.username)


@method_decorator(login_required, name='dispatch')
@method_decorator(Inject(service=services.FriendService), name='dispatch')
class Friends(View, ListMixin):
    SRVC_LST_METHOD = 'friends'

    def get(self, request: HttpRequest, service: services.FriendService) -> HttpResponse:
        friendships = super().get(request, service)
        extra_data = {
            'friends': [{
                'friend': friendship.initiated if friendship.initiator.pk==request.user.pk else friendship.initiator,
                'button': AddRemoveFriendButton.from_service(
                    request,
                    service,
                    request.user,
                    friendship.initiated if friendship.initiator.pk==request.user.pk else friendship.initiator
                ),
            } for friendship in friendships]
        }
        return render(request, 'friends.html', extra_data)


@method_decorator(login_required, name='dispatch')
@method_decorator(Inject(service=services.MessengerService), name='dispatch')
class Conversations(View, ListMixin):
    SRVC_LST_METHOD = 'list_mailboxes'

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
    SRVC_LST_METHOD = 'read_mailbox'
    SRVC_UPS_METHOD = 'send_message'

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
    SRVC_DTL_METHOD = 'assert_is_friend'
    SRVC_UPS_METHOD = 'send_message_to_friend'

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
    SRVC_DTL_METHOD = 'assert_can_see_meet'
    SRVC_UPS_METHOD = 'send_message_to_meet_organizer'

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
    SRVC_LST_METHOD = 'meets_by_popularity'

    def get(self, request: HttpRequest, service: services.MeetService):
        meets = super().get(request, service)
        return render(request, 'meets.html', {
            'meets': meets,
            'by': 'popularity',
        })


@method_decorator(Inject(service=services.MeetService), name='dispatch')
class MeetsNearby(View, ListMixin):
    SRVC_LST_METHOD = 'meets_by_distance'

    def get(self, request: HttpRequest, service: services.MeetService, lats: str = None, longs: str = None):
        reference_point = None
        try:
            longf = float(longs)
            latf = float(lats)
            reference_point = Point(longf, latf)
        except BaseException:
            try:
                return redirect('meets_nearby_precise', lats=request.GET['lat'], longs=request.GET['long'])
            except BaseException:
                return render(request, 'asklatlong.html', {'next': request.GET.get('next', resolve_url('meets_nearby'))})
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
    SRVC_DTL_METHOD = 'assert_can_see_meet'

    def get(self, request: HttpRequest, service: services.MeetService, meet: models.Meet):
        super().get(request, service, meet)
        return render(request, 'meet_view.html', {
            'meet': meet,
        })


@method_decorator(login_required, name='dispatch')
@method_decorator(Inject(service=services.MeetService), name='dispatch')
class MeetNew(View, UpsertMixin):
    SRVC_UPS_METHOD = 'add_update_meet'

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
    SRVC_DTL_METHOD = 'assert_can_edit_meet'
    SRVC_UPS_METHOD = 'add_update_meet'
    SRVC_DEL_METHOD = 'delete_meet'

    def get(self, request: HttpRequest, service: services.MeetService, meet: models.Meet):
        super().get(request, service, meet)
        form = forms.MeetForm({**meet.__dict__, 'lng': meet.point.y, 'lat': meet.point.x}, instance=meet)
        return render(request, 'meet_edit.html', {
            'form': form,
            'meet': meet,
        })

    def post(self, request: HttpRequest, service: services.MeetService, meet: models.Meet):
        form = forms.MeetForm(request.POST)
        try:
            super().post(request, service, form)
        except services.FormValidationFailedException:
            return render(request, 'meet_edit.html', {
                'form': form,
                'meet': meet,
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
    SRVC_LST_METHOD = 'meet_links'
    SRVC_UPS_METHOD = 'meet_save_external_link'

    def get(self, request: HttpRequest, service: services.MeetService, meet: models.Meet):
        mels = super().get(request, service, meet=meet)
        return render(request, 'meet_external_links_edit.html', {
            'meet': meet,
            'mels': mels,
            'form': forms.MeetExternalLinksForm(),
        })

    def post(self, request: HttpRequest, service: services.MeetService, meet: models.Meet):
        form = forms.MeetExternalLinksForm(request.POST)
        try:
            super().post(request, service, form, meet=meet)
        except services.FormValidationFailedException:
            return render(request, 'meet_external_links_edit.html', {
                'meet': meet,
                'form': form,
            })
        return redirect('meetlinks', key=meet.key)


@method_decorator(ModelSolver(pk=models.MeetExternalLinks, to_raise=Http404(_('meet_not_found'))), name='dispatch')
@method_decorator(KeywordArgumentsRenamer(pk='mel'), name='dispatch')
@method_decorator(login_required, name='dispatch')
@method_decorator(Inject(service=services.MeetService), name='dispatch')
class MeetLinkEdit(View, DetailsMixin, UpsertMixin, DeleteMixin):
    SRVC_DTL_METHOD = 'assert_can_edit_meet_external_link'
    SRVC_UPS_METHOD = 'meet_save_external_link'
    SRVC_DEL_METHOD = 'meet_delete_external_link'

    def get(self, request: HttpRequest, service: services.MeetService, mel: models.MeetExternalLinks):
        super().get(request, service, mel)
        return render(request, 'meet_external_link_edit.html', {
            'mel': mel,
            'form': forms.MeetExternalLinksForm(instance=mel),
        })

    def post(self, request: HttpRequest, service: services.MeetService, mel: models.MeetExternalLinks):
        form = forms.MeetExternalLinksForm(request.POST)
        try:
            super().post(request, service, form, meet=mel.parent)
        except services.FormValidationFailedException:
            return render(request, 'meet_external_link_edit.html', {
                'mel': mel,
                'form': form,
            })
        return redirect('meetlinks', key=mel.parent.key)

    def delete(self, request: HttpRequest, service: services.MeetService, mel: models.MeetExternalLinks):
        super().delete(request, service, mel)
        return redirect('meetlinks', key=mel.parent.key)


class MeetStarButton(TemplatePageComponentFixed):
    template_name = 'meetstarbutton.html'

    def __init__(self, request: HttpRequest, meet, has_star):
        super().__init__(request)
        self.meet = meet
        self.has_star = has_star is not None
        self.star_privacy = has_star.anonymous if has_star is not None else None
        self.star = has_star

    def get_context_data(self, **kwargs):
        stardict = dict() if self.star is None else self.star.__dict__
        return super().get_context_data(**dict(
            meet=self.meet,
            hasStar=self.has_star,
            star=self.star,
            starPrivacy=self.star_privacy,
            anonymousForm=forms.MeetStarForm({**stardict, 'anonymous': True}, instance=self.star),
            publicForm=forms.MeetStarForm({**stardict, 'anonymous': False}, instance=self.star)
        ), **kwargs)


@method_decorator(login_required, name='post')
@method_decorator(ModelSolver(key=models.Meet, to_raise=Http404(_('meet_not_found'))), name='dispatch')
@method_decorator(KeywordArgumentsRenamer(key='meet'), name='dispatch')
@method_decorator(Inject(service=services.MeetService), name='dispatch')
class MeetStars(View, ListMixin, UpsertMixin):
    SRVC_LST_METHOD = 'meet_stars'
    SRVC_UPS_METHOD = 'add_update_star'

    def get(self, request: HttpRequest, service: services.MeetService, meet: models.Meet):
        stars = super().get(request, service, meet=meet)
        return render(request, 'meetstars.html', {
            'meet': meet,
            'stars': stars,
            'button': MeetStarButton(request, meet, service.has_star(request.user, meet)),
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
                'button': MeetStarButton(request, meet, service.has_star(request.user, meet)),
            })
        return redirect('meetstars', key=meet.key)


@method_decorator(login_required, name='dispatch')
@method_decorator(ModelSolver(pk=models.MeetStar, to_raise=Http404(_('meetstar_not_found'))), name='dispatch')
@method_decorator(KeywordArgumentsRenamer(pk='meet_star'), name='dispatch')
@method_decorator(Inject(service=services.MeetService), name='dispatch')
class MeetStarEdit(View, DeleteMixin):
    SRVC_DEL_METHOD = 'remove_star'

    def delete(self, request: HttpRequest, service: services.MeetService, meet_star: models.MeetStar):
        super().delete(request, service, meet_star)
        return redirect('meetstars', key=meet_star.meet.key)


@method_decorator(Inject(service=services.MeetService), name='dispatch')
class MeetHints(View, ListMixin):
    SRVC_LST_METHOD = 'place_suggestions'

    def get(self, request: HttpRequest, service: services.MeetService):
        hint = request.GET.get('for', '')
        hints = super().get(request, service, plchnt=hint)
        return JsonResponse({'hints': [hint.__dict__ for hint in hints]})


class LDDump(TemplateView):
    template_name = 'lddump.html'


@method_decorator(Inject(service=services.LDService), name='dispatch')
class LDDumpDownload(View):
    def get(self, request: HttpRequest, service: services.LDService, fmt: str = 'rdf'):
        g = service.dump_all(request.user)
        data, mime = service.serialize(request.user, g, fmt)
        return HttpResponse(data, content_type=mime)


@method_decorator(Inject(service=services.LDService), name='dispatch')
class LDSchema(View):
    def get(self, request: HttpRequest, service: services.LDService, fmt: str = 'rdf'):
        g = service.schema(request.user)
        data, mime = service.serialize(request.user, g, fmt)
        return HttpResponse(data, content_type=mime)


@method_decorator(Inject(service=services.LDService), name='dispatch')
class LDModelBuild(View):
    def get(self, request: HttpRequest, service: services.LDService, model: str, pk: int, fmt: str):
        g = service.dump_instance(request.user, model, pk)
        data, mime = service.serialize(request.user, g, fmt)
        return HttpResponse(data, content_type=mime)


class SparqlReverseProxy(TemplateView):
    template_name = 'sparql_reverseproxy.html'

    def get(self, request, *args, **kwargs):
        if request.GET.get('query', ''):
            u = f'http://localhost:64164/meet/sparql?{urlencode(request.GET)}'
            r = requests.get(url=u, params={'Accept': request.META.get('HTTP_ACCEPT', 'application/json; encoding=UTF-8')})
            return HttpResponse(
                content=r.content,
                status=r.status_code,
                content_type=r.headers['Content-Type']
            )
        else:
            return super().get(request, *args, **kwargs)


class Sparql(TemplateView):
    template_name = 'sparql.html'
    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(*args, **{
            **kwargs,
            'samplequery': (
                'PREFIX schm: <' + services.LDService().schemaNS() + '>' + '\n' +
                'PREFIX mere: <http://ontology.eil.utoronto.ca/icity/Mereology/>' + '\n' +
                'PREFIX dbp: <http://dbpedia.org/property/>' + '\n' +
                'PREFIX dul: <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>' + '\n' +
                'PREFIX cc: <http://creativecommons.org/ns#>' + '\n' +
                'PREFIX rel: <http://purl.org/vocab/relationship/>' + '\n' +
                'PREFIX dbo: <http://dbpedia.org/ontology/>' + '\n' +
                'PREFIX foaf: <http://xmlns.com/foaf/0.1/>' + '\n' +
                'PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>' + '\n' +
                'PREFIX owl: <http://www.w3.org/2002/07/owl#>' + '\n' +
                'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>' + '\n' +
                'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>' + '\n' +
                '\n' +
                'SELECT ?subject ?predicate ?object' + '\n' +
                'WHERE {' + '\n' +
                '    ?subject ?predicate ?object .' + '\n' +
                '}' + '\n' +
                'LIMIT 25'
            ),
        })
