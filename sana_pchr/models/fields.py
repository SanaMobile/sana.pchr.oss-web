from django.db import models
import base64
from sana_pchr.crypto import Credential, DerivedCredential
import datetime
import pytz
import uuid


# Class containing static functions for calling
class DefaultFuncs:
    # Added all the callable default functions here so Callables work with Migrations.
    @staticmethod
    def getNow():
        return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

    @staticmethod
    def make_uuid():
        return uuid.uuid4().hex

    @staticmethod
    def far_future():
        return datetime.datetime(9000, 12, 31, 23, 59, 59, 999999, tzinfo=pytz.utc)


class UUIDField(models.Field, metaclass=models.SubfieldBase):
    def __init__(self, *args, **kwargs):
        # We don't pass the callable itself as a default since that makes it hard to mock
        kwargs["default"] = DefaultFuncs.make_uuid
        kwargs["max_length"] = 36
        super(UUIDField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'


class CredentialField(models.Field, metaclass=models.SubfieldBase):
    def __init__(self, *args, **kwargs):
        kwargs["default"] = Credential.generate
        kwargs["editable"] = False
        super(CredentialField, self).__init__(*args, **kwargs)

    def to_python(self, value, metaclass=models.SubfieldBase):
        if isinstance(value, Credential):
            return value

        bin_key = super(CredentialField, self).to_python(value)
        return Credential(bin_key)

    def get_prep_value(self, value):
        return super(CredentialField, self).get_prep_value(value.key if value and hasattr(value, "key") else value)

    def get_internal_type(self):
        return 'BinaryField'


class DerivedCredentialField(models.Field, metaclass=models.SubfieldBase):
    def __init__(self, *args, **kwargs):
        kwargs["editable"] = False
        kwargs["max_length"] = 128
        super(DerivedCredentialField, self).__init__(*args, **kwargs)

    def to_python(self, value, metaclass=models.SubfieldBase):
        if isinstance(value, Credential):
            return value

        ser_rep = super(DerivedCredentialField, self).to_python(value)
        if not ser_rep or len(ser_rep.split('$', 3)) != 4:
            return
        algm, iterations, salt, key = ser_rep.split('$', 3)
        return DerivedCredential(key=base64.b64decode(key), iterations=int(iterations), salt=salt)

    def get_prep_value(self, value):
        serialized = "%s$%d$%s$%s" % (value.algorithm, value.iterations, value.salt,
                                      base64.b64encode(value.key).decode('ascii').strip()) if value and hasattr(value,
                                                                                                                "key") else value
        return super(DerivedCredentialField, self).get_prep_value(serialized)

    def get_internal_type(self):
        return 'CharField'
