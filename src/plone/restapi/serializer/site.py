# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IPloneSiteRoot, Interface)
class SerializeSiteRootToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _query_for_children(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        query = {'path': {'depth': 1, 'query': path}}
        return catalog(query)

    def __call__(self):
        result = {
            # '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            '@id': self.context.absolute_url(),
            '@type': 'Plone Site',
            'parent': {},
        }
        brains = self._query_for_children()
        result['member'] = [
            getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
            for brain in brains
        ]
        return result
