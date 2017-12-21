import hashlib
from django.forms import ModelForm, CharField

from sana_pchr.models.app import App

class AppForm(ModelForm):
    ''' Mobile client application package '''
    class Meta:
        model = App
        fields = [
            'version',
            'pkg',
        ]
        
    def __init__(self, *args, **kwargs):
        super(AppForm, self).__init__(*args, **kwargs)
            
    def save(self, *args, **kwargs):
        md5 = hashlib.md5()
        for chunk in self.instance.pkg.chunks():
            md5.update(chunk)
        self.instance.checksum = md5.hexdigest()
        res = super(AppForm, self).save(*args, **kwargs)
        return res
