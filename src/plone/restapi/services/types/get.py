# -*- coding: utf-8 -*-
from plone.rest import Service
from plone.restapi.types.utils import get_jsonschema_for_portal_type

from zope.component import getUtility
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import IVocabularyFactory


class TypesGet(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(TypesGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    @property
    def _get_record_name(self):
        if len(self.params) != 1:
            raise Exception(
                "Must supply exactly one parameter (dotted name of"
                "the record to be retrieved)")

        return self.params[0]

    def render(self):
        if self.params and len(self.params) > 0:
            self.request.response.setHeader(
                "Content-Type",
                "application/json+schema"
            )
            try:
                portal_type = self.params.pop()
                return get_jsonschema_for_portal_type(
                    portal_type,
                    self.context,
                    self.request
                )
            except KeyError:
                self.request.response.setHeader(
                    "Content-Type",
                    "application/json"
                )
                self.request.response.setStatus(404)
                return {
                    'type': 'NotFound',
                    'message': 'Type "{}" could not be found.'.format(
                        portal_type
                    )
                }
        vocab_factory = getUtility(
            IVocabularyFactory,
            name="plone.app.vocabularies.ReallyUserFriendlyTypes"
        )
        return [
            {
                '@id': '{}/@types/{}'.format(
                    self.context.absolute_url(),
                    x.token
                ),
                'title': x.value
            } for x in vocab_factory(self.context)
        ]
