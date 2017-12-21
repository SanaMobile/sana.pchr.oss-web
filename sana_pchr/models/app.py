import hashlib

from django.db import models

from .device import Device

__all__ = [
    'App',
    'InstalledApp',
    ]

class App(models.Model):
    ''' Mobile client application package '''
    class Meta:
        ordering = ['-version']
        
    version = models.PositiveIntegerField()
    pkg = models.FileField(upload_to='app/', blank=True)
    checksum = models.CharField(max_length=64, blank=True)

    def save(self, *args, **kwargs):
        # Calculate the checksum if the file is specified
        if self.pkg:
            md5 = hashlib.md5()
            for chunk in self.pkg.chunks():
                md5.update(chunk)
            self.checksum = md5.hexdigest()
            # Do not want to save an actual file
            self.pkg = ""
        return super(App,self).save(*args,**kwargs)

class InstalledApp(models.Model):
    ''' Records currently installed application versions in clients '''
    device = models.ForeignKey(Device, db_column="device_uuid")
    version = models.PositiveIntegerField()

