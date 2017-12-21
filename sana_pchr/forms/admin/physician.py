from django.forms import ModelForm, CharField
from ..widgets import QRWidget
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from sana_pchr.models import Physician


class PhysicianForm(ModelForm):
    PIN = CharField(max_length=4, required=False, label="Reset PIN")

    qr = CharField(widget=QRWidget, label="QR Code", required=False)

    def __init__(self, *args, **kwargs):
        super(PhysicianForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields["qr"].initial = self.instance.qr_contents
        else:
            del self.fields["qr"]

    def save(self, *args, **kwargs):
        unhashed_pin = self.cleaned_data.get('PIN', None)

        if unhashed_pin:
            hasher = PBKDF2PasswordHasher()
            self.instance.hashedPIN = hasher.encode(unhashed_pin, hasher.salt())

        res = super(PhysicianForm, self).save(*args, **kwargs)
        return res

    class Meta:
        fields = ["firstName", "lastName", "PIN", "email", "phone", "picture", "recovery_question", "recovery_answer",
                  "clinics", "type"]
        model = Physician
