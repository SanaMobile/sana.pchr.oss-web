from apscheduler.schedulers.background import BackgroundScheduler

from django.conf import settings

from sana.pchr.utils import smslib

sched = BackgroundScheduler()

# Remove this prior to production release
#@sched.scheduled_job('interval', minutes=1)
#def timed_job():
#    print('This job is run every one minutes.')
    
@sched.scheduled_job('cron', day_of_week='mon-sun', hour=settings.SMS_SEND_TIME)
def scheduled_reminder():
    messages = smslib.get_messages(fromSMS=settings.SMS_SENDER)
    for message in messages:
        smslib.send_sms(settings.SMS_API_URL,
            settings.SMS_API_USERNAME,
            settings.SMS_API_PASSWORD,
            message)

#sched.start()
