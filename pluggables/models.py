from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.http import HttpRequest
from pluggables.utils.picklefield import PickledObjectField

class PluggableManager(models.Manager):
    def pluggable(self, request):
        return self.filter(pluggable_url=request.pluggable.pluggable_url_data)

class PluggableModel(models.Model):
    def __init__(self, *args, **kwargs):
        if len(args) >= 1 and isinstance(args[0], HttpRequest):
            self.set_pluggable_url(args[0])
            args = args[1:]
        super(PluggableModel, self).__init__(*args, **kwargs)

    pluggable_url = PickledObjectField(blank=True)

    objects = PluggableManager()

    def set_pluggable_url(self, request):
        if request and hasattr(request, 'pluggable'):
            self.pluggable_url = request.pluggable.pluggable_url_data

    class Meta:
        abstract = True

class PluggableObjectManager(PluggableManager):
    def pluggable_object(self, request):
        if request.pluggable.view_context is None:
            return self.filter(pluggable_content_type__isnull=True, pluggable_object_id__isnull=True)
        else:
            content_type = ContentType.objects.get_for_model(request.pluggable.view_context)
            return self.filter(pluggable_content_type=content_type, pluggable_object_id=request.pluggable.view_context.pk)

class PluggableObjectModel(PluggableModel):
    def __init__(self, *args, **kwargs):
        if len(args) >= 1 and isinstance(args[0], HttpRequest):
            self.set_pluggable_url(args[0])
            self.set_pluggable_object(args[0])
        super(PluggableObjectModel, self).__init__(*args, **kwargs)

    pluggable_content_type = models.ForeignKey(ContentType, null=True, blank=True)
    pluggable_object_id = models.PositiveIntegerField(null=True, blank=True)

    pluggable_object = generic.GenericForeignKey(fk_field='pluggable_object_id', ct_field='pluggable_content_type')

    objects = PluggableObjectManager()


    def set_pluggable_object(self, request):
        if request and hasattr(request, 'pluggable'):
            self.pluggable_object = request.pluggable.view_context

    class Meta:
        abstract = True
