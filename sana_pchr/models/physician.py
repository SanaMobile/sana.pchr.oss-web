from django.db import models
from .fields import CredentialField, DerivedCredentialField
from sana_pchr.crypto import NormalizedDerivedCredential
from .base import SynchronizedModel
import uuid
import base64


class Physician(SynchronizedModel):
    firstName = models.CharField(max_length=45, blank=False)
    lastName = models.CharField(max_length=45, blank=False)
    picture = models.ImageField(blank=True)
    # Use PBKDF2PasswordHasher for PIN hashing
    hashedPIN = models.CharField(max_length=128, blank=False)
    email = models.EmailField(max_length=254, blank=True, db_index=True)
    phone = models.CharField(max_length=45, blank=True, db_index=True)
    # In the future we might have more, in which case an outboard table would be merited
    recovery_question = models.CharField(default="Default password:", max_length=45, blank=False)
    recovery_answer = models.CharField(default="sanapchr", max_length=45, blank=False)
    # The key derivation is designed to be slow, but we don't want to incur that overhead here
    # So, we cache the key
    recovery_key = DerivedCredentialField(blank=True, null=True)
    key = CredentialField(blank=False)
    clinics = models.ManyToManyField("Clinic", through="Clinic_Physician", blank=False)

    # Used for Dr, Nurse, etc.
    type = models.CharField(max_length=1, default="D")

    @property
    def qr_contents(self):
        # Had to make this base64-encoded because none all of the Android QR scanning libraries could stomach the raw binary
        # Maybe in the future it can be switched back - hence the leading NULL for differentiation.
        return base64.b64encode(b"\0" + uuid.UUID(self.uuid).bytes + self.key._key)

    def save(self, *args, **kwargs):
        # Update the recovery_key
        if self.recovery_answer:
            self.recovery_key = NormalizedDerivedCredential(self.recovery_answer)
        return super(Physician, self).save(*args, **kwargs)

    def __str__(self):
        return "%s %s" % (self.firstName, self.lastName)
