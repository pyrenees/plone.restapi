# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from Products.Archetypes.interfaces import IBaseFolder
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IBaseObject, Interface)
class SerializeToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        parent = aq_parent(aq_inner(self.context))
        parent_summary = getMultiAdapter(
            (parent, self.request), ISerializeToJsonSummary)()
        result = {
            # '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            '@id': self.context.absolute_url(),
            '@type': self.context.portal_type,
            'parent': parent_summary,
            'UID': self.context.UID(),
        }

        obj = self.context
        for field in obj.Schema().fields():

            if 'r' not in field.mode or not field.checkPermission('r', obj):
                continue

            name = field.getName()

            serializer = queryMultiAdapter(
                (field, self.context, self.request),
                IFieldSerializer)
            if serializer is not None:
                result[name] = serializer()

        return result


@implementer(ISerializeToJson)
@adapter(IBaseFolder, Interface)
class SerializeFolderToJson(SerializeToJson):

    def _query_for_children(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        query = {'path': {'depth': 1, 'query': path}}
        return catalog(query)

    def __call__(self):
        result = super(SerializeFolderToJson, self).__call__()
        children = self._query_for_children()
        result['member'] = [
            getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
            for brain in children
        ]
        return result
