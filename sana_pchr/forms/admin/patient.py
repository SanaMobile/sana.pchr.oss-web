from django.forms import ModelForm, CharField
from ..widgets import QRWidget
from sana_pchr.models import Patient


class PatientForm(ModelForm):
    
    qr = CharField(widget=QRWidget, label="QR Code", required=False)

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields["qr"].initial = self.instance.qr_contents
        else:
            del self.fields["qr"]

    class Meta:
        fields = ["firstName", "lastName", "UNHCR", "birthYear", "birthCity", "gender", "provider_id",
                  "phone", "physicians"]
        model = Patient
