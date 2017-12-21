from restless.serializers import JSONSerializer
from restless.utils import MoreTypesJSONEncoder
import uuid
import json


class EvenMoreTypesJSONEncoder(MoreTypesJSONEncoder):
    # This is one of the most annoying parts of the python JSON serializer - you have to implement custom serializations in the serializer, not in the serialized classes
    # C#'s ISerializable is a much nicer approach in this regard
    def default(self, data):
        if isinstance(data, uuid.UUID):
            return str(data)
        return super(EvenMoreTypesJSONEncoder, self).default(data)


class AugmentedJSONSerializer(JSONSerializer):
    def serialize(self, data):
        return json.dumps(data, cls=EvenMoreTypesJSONEncoder)
