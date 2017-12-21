from django.db import models
from datetime import date
from sana_pchr.models.fields import DefaultFuncs
from .fields import UUIDField, DefaultFuncs


class Base(models.Model):
    uuid = UUIDField(primary_key=True)

    class Meta:
        abstract = True


class SynchronizedModel(Base):
    deleted = models.DateTimeField(default=DefaultFuncs.far_future())
    created = models.DateTimeField(default=DefaultFuncs.getNow)
    updated = models.DateTimeField(default=DefaultFuncs.getNow)
    # Don't use auto_now since I'm nervous about this field being updated outside of the synchronization logic
    # Don't use auto_now_add since it makes unit testing a pain (can't override the value during creation)
    synchronized = models.DateTimeField(default=DefaultFuncs.getNow)

    def save(self, *args, **kwargs):
        self.updated = DefaultFuncs.getNow()
        self.synchronized = DefaultFuncs.getNow()
        return super(SynchronizedModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class CategoryModel(SynchronizedModel):
    displayName = models.CharField(max_length=127)
    displayNameAr = models.CharField(max_length=127, default = "")
    priority = models.IntegerField(default=1)

    def __str__(self):
        return self.displayName + " " + self.displayNameAr;

    class Meta:
        abstract = True


class SynchronizedThroughModel(models.Model):
    uuid = models.CharField(max_length=36, primary_key=True, null=False, blank=False)
    deleted = models.DateTimeField(default=DefaultFuncs.far_future())
    created = models.DateTimeField(default=DefaultFuncs.getNow)
    updated = models.DateTimeField(default=DefaultFuncs.getNow)
    # Don't use auto_now since I'm nervous about this field being updated outside of the synchronization logic
    # Don't use auto_now_add since it makes unit testing a pain (can't override the value during creation)
    synchronized = models.DateTimeField(default=DefaultFuncs.getNow)

    class Meta:
        abstract = True
