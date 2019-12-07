# -*- encoding: utf-8 -*-

from io import BytesIO
from typing import Tuple
from pycdi.utils import Singleton
from .FriendService import FriendService
from .MeetService import MeetService
from .MessengerService import MessengerService
from .exceptions import NotFoundException
from .exceptions import NotAuthorizedException
from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from .. import models
from ...adminModelRegister import classes_in_module
from ...objectify import Objectify

import rdflib

from rdflib import Literal

from rdflib.namespace import OWL
from rdflib.namespace import RDF
from rdflib.namespace import RDFS
from rdflib.namespace import FOAF
from rdflib.namespace import URIRef
from rdflib.namespace import Namespace

from rdflib.plugins.serializers.n3 import N3Serializer
from rdflib.plugins.serializers.nt import NTSerializer
from rdflib.plugins.serializers.trix import TriXSerializer
from rdflib.plugins.serializers.trig import TrigSerializer
from rdflib.plugins.serializers.rdfxml import XMLSerializer
from rdflib.plugins.serializers.turtle import TurtleSerializer

PURL_REL = Namespace('http://purl.org/vocab/relationship/')
PURL_RES = Namespace('http://purl.org/vocab/resourcelist/schema#')
DUL = Namespace('http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#')
WIKIDATA = Namespace('http://www.wikidata.org/entity/')
DBO = Namespace('http://dbpedia.org/ontology/')
DBP = Namespace('http://dbpedia.org/property/')
GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
MERE = Namespace('http://ontology.eil.utoronto.ca/icity/Mereology/')
CCNS = Namespace('http://creativecommons.org/ns#')
WRCC = Namespace('http://web.resource.org/cc/')


@Singleton()
class LDService:
    def __init__(self):
        self.services = Objectify({'meet': None, 'friend': None, 'messenger': None})
        self.services.meet = MeetService()
        self.services.friend = FriendService()
        self.services.messenger = MessengerService()

    serializers = {
        'ttl': (TurtleSerializer, 'text/turtle'),
        'n3': (N3Serializer, 'text/n3'),
        'nt': (NTSerializer, 'application/n-triples'),
        'trix': (TriXSerializer, 'text/xml'),
        'trig': (TrigSerializer, 'application/trig'),
        'rdf': (XMLSerializer, 'application/rdf+xml'),
    }

    allowed_models = {
        model.__name__.lower(): model
        for model in classes_in_module(models)
    }

    def serialize(self, user, graph, ffmt) -> Tuple[str, str]:
        if ffmt not in type(self).serializers:
            ffmt = 'rdf'
        Serializer, mime = type(self).serializers[ffmt]
        sio = BytesIO()
        Serializer(graph).serialize(sio)
        return (sio.getvalue().decode(), mime)

    def dump_all(self, user) -> rdflib.Graph:
        g = rdflib.Graph()
        for u in models.User.objects.all():
            self.dump_instance(user, u, g=g)  # User
        for m in self.services.meet.all_viewable_meets(user):
            self.dump_instance(user, m, g=g)  # Meet
            for l in m.external_links.all():
                self.dump_instance(user, l, g=g)  # Meet External Link
        for b in self.services.messenger.list_mailboxes(user):
            self.dump_instance(user, b, g=g)  # Mailbox
            for m in b.messages.all():
                self.dump_instance(user, m, g=g)  # Message
        return g

    def dump_instance(self, user, modelname, modelpk=None, g: rdflib.Graph = None) -> rdflib.Graph:
        instance = modelname
        if not hasattr(modelname, 'pk'):
            desired_model = type(self).allowed_models.get(modelname.lower(), None)
            if desired_model is None:
                print(type(self).allowed_models)
                raise NotFoundException(_('The requested model was not found.'))
            instance = desired_model.objects.filter(id=modelpk).first()
            if instance is None:
                raise NotFoundException(_('The requested instance was not found.'))
        if g is None:
            g = rdflib.Graph()
        self._serizize(user, instance, g)
        return g
    
    def uri_of(self, instance) -> URIRef:
        host = settings.ALLOWED_HOSTS[0]
        host = 'localhost:8000' if host=='*' else host
        return URIRef(f'https://{host}{reverse("ldmodelbuild", args=[instance.__class__.__name__, instance.pk, "rdf"])}')

    def _serizize(self, user, instance, g):
        thisuri = self.uri_of(instance)
        if isinstance(instance, models.User):
            g.add((thisuri, RDF.type, OWL.Thing))
            g.add((thisuri, RDF.type, FOAF.Person))
            g.add((thisuri, RDF.type, DBO.Agent))
            g.add((thisuri, RDFS.label, Literal(instance.username)))
            g.add((thisuri, FOAF.name, Literal(instance.username)))
            for friend in self.services.friend.established_friends(instance):
                otheruri = self.uri_of(friend.initiator if friend.initiated.pk == instance.pk else friend.initiated)
                g.add((thisuri, FOAF.knows, otheruri))
                g.add((thisuri, PURL_REL.knowsOf, otheruri))
                g.add((thisuri, PURL_REL.friendOf, otheruri))
            for meet in self.services.meet.all_viewable_meets(user).filter(creator=instance).all():
                otheruri = self.uri_of(meet)
                g.add((thisuri, DUL.isParticipantIn, otheruri))
            for star in instance.stars.filter(anonymous=False).all():
                otheruri = self.uri_of(star.meet)
                g.add((thisuri, DUL.isParticipantIn, otheruri))
                g.add((thisuri, PURL_REL.participantIn, otheruri))
            for mbox in self.services.messenger.list_mailboxes(instance):
                otheruri = self.uri_of(mbox)
                g.add((thisuri, MERE.containedIn, otheruri))
                g.add((thisuri, PURL_REL.participantIn, otheruri))
                g.add((thisuri, PURL_REL.usesList, otheruri))
            g.add((thisuri, CCNS.prohibits, CCNS.Sharing))
            g.add((thisuri, CCNS.prohibits, CCNS.DerivativeWorks))
            g.add((thisuri, CCNS.prohibits, CCNS.Reproduction))
            g.add((thisuri, CCNS.prohibits, CCNS.Distribution))
            g.add((thisuri, CCNS.prohibits, CCNS.CommercialUse))
        elif isinstance(instance, models.ChatMailbox):
            self.services.messenger.assert_mailbox_readable(user, instance)
            g.add((thisuri, RDF.type, OWL.Thing))
            g.add((thisuri, RDF.type, DBO.List))
            g.add((thisuri, RDF.type, PURL_RES.List))
            g.add((thisuri, PURL_REL.participant, self.uri_of(instance.initiator)))
            g.add((thisuri, PURL_REL.participant, self.uri_of(instance.initiated)))
            if instance.meet is not None:
                g.add((thisuri, RDFS.seeAlso, self.uri_of(instance.meet)))
            for message in instance.messages.all():
                otheruri = self.uri_of(message)
                g.add((thisuri, MERE.hasProperPart, otheruri))
                g.add((thisuri, MERE.contains, otheruri))
            g.add((thisuri, CCNS.prohibits, CCNS.Sharing))
            g.add((thisuri, CCNS.prohibits, CCNS.DerivativeWorks))
            g.add((thisuri, CCNS.prohibits, CCNS.Reproduction))
            g.add((thisuri, CCNS.prohibits, CCNS.Distribution))
            g.add((thisuri, CCNS.prohibits, CCNS.CommercialUse))
        elif isinstance(instance, models.ChatMessage):
            self.services.messenger.assert_mailbox_readable(user, instance.mailbox)
            g.add((thisuri, RDF.type, OWL.Thing))
            g.add((thisuri, RDF.type, DBO.Letter))
            g.add((thisuri, MERE.properPartOf, self.uri_of(instance.mailbox)))
            g.add((thisuri, MERE.containedIn, self.uri_of(instance.mailbox)))
            g.add((thisuri, DBP.author, self.uri_of(instance.sender)))
            g.add((thisuri, DBP.firstPublicationDate, Literal(instance.sent)))
            g.add((thisuri, DBP.lastPublicationDate, Literal(instance.sent)))
            g.add((thisuri, DBP.unicode, Literal(instance.message)))
            g.add((thisuri, CCNS.prohibits, CCNS.Sharing))
            g.add((thisuri, CCNS.prohibits, CCNS.DerivativeWorks))
            g.add((thisuri, CCNS.prohibits, CCNS.Reproduction))
            g.add((thisuri, CCNS.prohibits, CCNS.Distribution))
            g.add((thisuri, CCNS.prohibits, CCNS.CommercialUse))
        elif isinstance(instance, models.MeetExternalLinks):
            g.add((thisuri, RDF.type, OWL.Thing))
            g.add((thisuri, RDF.type, DBO.Reference))
            g.add((thisuri, MERE.properPartOf, self.uri_of(instance.parent)))
            g.add((thisuri, MERE.containedIn, self.uri_of(instance.parent)))
            g.add((thisuri, RDFS.label, Literal(instance.name)))
            g.add((thisuri, RDFS.seeAlso, Literal(instance.url)))
            g.add((thisuri, DBP.reference, Literal(instance.url)))
            g.add((thisuri, CCNS.permission, CCNS.Sharing))
            g.add((thisuri, CCNS.permission, CCNS.DerivativeWorks))
            g.add((thisuri, CCNS.permission, CCNS.Reproduction))
            g.add((thisuri, CCNS.prohibits, CCNS.Distribution))
            g.add((thisuri, CCNS.prohibits, CCNS.CommercialUse))
        elif isinstance(instance, models.Meet):
            self.services.meet.assert_can_see_meet(user, instance)
            g.add((thisuri, RDF.type, OWL.Thing))
            g.add((thisuri, RDF.type, DBO.Event))
            g.add((thisuri, RDF.type, DUL.Event))
            g.add((thisuri, RDF.type, WIKIDATA.Q1656682))  # Event
            g.add((thisuri, RDFS.label, Literal(instance.title)))
            g.add((thisuri, DBP.name, Literal(instance.title)))
            g.add((thisuri, RDFS.comment, Literal(instance.description)))
            g.add((thisuri, DBO.abstract, Literal(instance.description)))
            g.add((thisuri, DBP.organizer, self.uri_of(instance.creator)))
            g.add((thisuri, DBO.location, Literal(instance.name)))
            g.add((thisuri, DBP.venue, Literal(instance.name)))
            g.add((thisuri, DBO.startDateTime, Literal(instance.meeting)))
            g.add((thisuri, GEO.geometry, Literal(f'POINT({instance.point.x} {instance.point.y})')))
            g.add((thisuri, DBP.longitude, Literal(instance.point.x)))
            g.add((thisuri, DBP.latitude, Literal(instance.point.y)))
            for star in instance.stars.filter(anonymous=False).all():
                otheruri = self.uri_of(star.owner)
                g.add((thisuri, DUL.hasParticipant, otheruri))
                g.add((thisuri, PURL_REL.participant, otheruri))
            g.add((thisuri, CCNS.permission, CCNS.Sharing))
            g.add((thisuri, CCNS.permission, CCNS.DerivativeWorks))
            g.add((thisuri, CCNS.permission, CCNS.Reproduction))
            g.add((thisuri, CCNS.prohibits, CCNS.Distribution))
            g.add((thisuri, CCNS.prohibits, CCNS.CommercialUse))
        else:
            raise NotAuthorizedException(_('The requested data cannot be served.'))
