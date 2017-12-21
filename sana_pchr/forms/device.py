from django.forms import ModelForm
from sana_pchr.models import Device


class DeviceForm(ModelForm):
    def clean_deviceMAC(self):
        return self.cleaned_data["deviceMAC"].upper()

    class Meta:
        model = Device
        fields = ['name', 'deviceMAC']
