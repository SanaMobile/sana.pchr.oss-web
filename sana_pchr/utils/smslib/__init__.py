from . import content
from . import globesms
from .messages import *
from .response import *

__all__ = [
    'utf8_encode',
    'SMSMessage',
    'SMSResponse',
    'get_messages',
    'send_sms'
]

def get_messages(fromSMS=None):
    return content.get_content(fromSMS)

def send_sms(url, username, password, sms_message):
    return globesms.send_sms(url,username,password, sms_message)
