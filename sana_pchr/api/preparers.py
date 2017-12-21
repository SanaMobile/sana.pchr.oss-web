from restless.preparers import FieldsPreparer


class LambdaFieldsPreparer(FieldsPreparer):
    def lookup_data(self, lookup, data):
        if callable(lookup):
            return lookup(data)
        return super(LambdaFieldsPreparer, self).lookup_data(lookup, data)


class SynchronizedFieldsPreparer(LambdaFieldsPreparer):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("fields", {}).update({
            "uuid": "uuid",
            "created": "created",
            "updated": "updated",
            "synchronized": "synchronized",
            "deleted": "deleted"
        })

        return super(SynchronizedFieldsPreparer, self).__init__(*args, **kwargs)

