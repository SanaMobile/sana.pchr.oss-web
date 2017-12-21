
__all__ = [
    'SMSResponse',
]

class SMSResponse(object):

    status = None
    message = None

    def __init__(self, status, message):
        self.status = status
        self.message = message

    def __unicode__(self):
        return u"{0}: {1}".format(self.status,self.message)

