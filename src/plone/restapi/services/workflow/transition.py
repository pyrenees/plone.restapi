# -*- coding: utf-8 -*-
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from plone.rest import Service
from plone.restapi.deserializer import json_body
from plone.restapi.serializer.converters import json_compatible
from zope.i18n import translate
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound


class WorkflowTransition(Service):
    """Trigger workflow transition
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(WorkflowTransition, self).__init__(context, request)
        self.transition = None

    def publishTraverse(self, request, name):
        if self.transition is None:
            self.transition = name
        else:
            raise NotFound(self, name, request)
        return self

    def render(self):
        if self.transition is None:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='BadRequest',
                message='Missing transition'))

        data = json_body(self.request)
        if data.keys() not in [[], ['comment']]:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='BadRequest',
                message='Invalid body'))

        wftool = getToolByName(self.context, 'portal_workflow')

        try:
            wftool.doActionFor(self.context, self.transition, **data)
        except WorkflowException as e:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='WorkflowException',
                message=translate(e.message, context=self.request)))

        history = wftool.getInfoFor(self.context, "review_history")
        return json_compatible(history[-1])
