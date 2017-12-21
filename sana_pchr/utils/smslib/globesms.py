# Python 3 compat
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
from django.utils.http import urlquote

from .messages import utf8_encode
from .response import SMSResponse

__all__ = [
    'send_globesms',
    'send_sms',
]
        
def send_globesms(url, username, password, fromSMS, toSMS, text):
    ''' Sends and SMS message through the Globe SMS API

        Paramters
            url
                The GLobeSMS API url. Should generally use SMS_API_URL.
            username
                The username provided to connect to our services
            password 
                The password to the service
            fromSMS
                Sender ID of the message. The "from" field in the GlobeSMS API
                url
            toSMS
                Mobile Destination Number (can accept both local and 
                international format, i.e: 03xxxxxx or 9613xxxxxx
                without leading + or 00), to submit_Multi please separate numbers
                by comma. The 'to' field in the Globe SMS API url
            text
                The content to encode as a UTF-8 encoded Text Message  This must
                be either a unicode or str value
    '''
    data = {
        'username': username,
        'password': password,
        'from': fromSMS,
        'to': toSMS,
        'text': urlquote(utf8_encode(text))
    }
    url = url.format(**data)
    response = urllib2.urlopen(url)
    content = response.read().decode('utf8').split(':')
    return SMSResponse(content[0].strip(), content[1].strip())

def send_sms(url, username, password, sms_message):
    data = {
        'username': username,
        'password': password,
        'from': sms_message.fromSMS,
        'to': sms_message.toSMS,
        'text': urlquote(sms_message.utf8encode())
    }
    url = url.format(**data)
    response = urllib2.urlopen(url)
    content = response.read().decode('utf8').split(':')
    return SMSResponse(content[0].strip(), content[1].strip())

