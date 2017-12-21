
__all__ = [
    'utf8_encode',
    'SMSMessage',
]

def utf8_encode(message):
    if isinstance(message, bytes):
        return message.decode('utf-8')
    elif isinstance(message, str):
        # Must be encoded in UTF-8
        return message.encode('utf-8')
    else:
        raise TypeError("Requires str or bytes object")

class SMSMessage(object):

    def __init__(self, fromSMS, toSMS, message):
        self.fromSMS = fromSMS
        self.toSMS = toSMS
        self.message = message

    def utf8encode(self, **kwargs):
        if kwargs:
            msg = message.format(kwargs)
        else:
            msg = self.message
        return utf8_encode(msg)

    def append_message(self,message):
        self.message += message

    def add_line(self, new_line):
        self.append_message("\n" + new_line)

