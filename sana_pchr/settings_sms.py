# GlobeSMS specific. Change when sending to other sms gateway
SMS_API_URL = 'https://globesms.net/smshub/api.php?username={username}&password={password}&action=sendsms&from={from}&to={to}&text={text}'
SMS_API_USERNAME = ''
SMS_API_PASSWORD = ''
SMS_SENDER = ''

## TODO check system time setting on Heroku
## - If UTC add -7 to send in local Lebanon time
## (We don't want to send in the middle of the night!)
# remind at 8 AM(Lebanon = 1?)
SMS_SEND_TIME=13
