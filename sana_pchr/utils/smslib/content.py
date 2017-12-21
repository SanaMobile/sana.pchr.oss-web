import datetime
import pytz
from django.db.models.query import Prefetch, Q
from sana_pchr.models import *

MESSAGE_TIMEZONE = pytz.timezone('EET')

# TODO replace with uuid values? Will need to change Q() constructors in get_clinic_qs if we do
MESSAGE_CLINICS = [
    "Karagheusian",
    "Taalabaya",
    "Tyre",
]
RECORD_CATEGORY_FOLLOWUP_UUID = "49cc095c88a54599b28bd478e28b0de4"
RECORD_FOLLOW_UP_DATE_FOMAT = "%Y-%m-%d"
RECORD_CATEGORIES_BIOMETRICS = [
    "02129288e9924ad8878ba2de2275a05d",
    "99daaf48a0c9403caeb964d6a1962b2c",
    "df202805711a4f91b26e6e0b8d923132",
    "91264851f75647b2baa03fda645b9644",
    "148b84bfa5484f39988d01bcc46f0cff",
    "88676ce8608a437997b6d228f0e6376c",
    "a82942e3b50d4ab7900b80f7e2f6b781",
]
MESSAGE_INSTRUCTION_ONE = str(".ستتلقى رسائل تتضمن معلومات عن زيارتك .{clinic} هذا")
MESSAGE_INSTRUCTION_TWO = str("لا تحذفها وأحضرها عند زيارة الطبيب؛ ستساعد على فهم حالتك.")
MESSAGE_REMINDER_DATE_FORMAT = "%d/%m/%Y"

def get_clinic_qs():
    """ Returns a list of clinic uuid values for clinics whose patients
        will receive follow up reminder messages
    """
    q = Q()
    for clinic in MESSAGE_CLINICS:
        q = q | Q(name__iexact=clinic)
    return list(Clinic.objects.filter(q).values_list('uuid', flat=True))

def get_visits(record_category, record_value, clinics):
    """ Returns a QuerySet of visits which have a record with a 
        specified value and category and whose clinic value is in 
        clinics.
    """
    visit_q = Q(encounter__clinic__in=clinics)
    visit_q = visit_q & Q(encounter__record__category=record_category)
    visit_q = visit_q & Q(encounter__record__category=record_value)
    return Visit.objects.filter(visit_q).select_related('patient')

def get_instruction_message_1(fromSMS, visit):
    """ Returns a new SMSMessage corresponding to the contents of
        MESSAGE_INSTRUCTION_ONE.
    """
    message = MESSAGE_INSTRUCTION_ONE.format(clinic=visit.clinic)
    return SMSMessage(fromSMS, visit.patient.phone, message)

def get_instruction_message_2(fromSMS, visit):
    """ Returns a new SMSMessage corresponding to the contents of
        MESSAGE_INSTRUCTION_TWO.
    """
    message = MESSAGE_INSTRUCTION_TWO
    return SMSMessage(fromSMS, message)

# Functions which append message content
def append_patient(sms_message, patient):
    """ Appends patient name to message"""
    line_template = u"Name: {firstName} {lastName}"
    new_line = line_template.format(firstName=patient.firstName,
                        lastName=patient.lastName)
    sms_message.add_line(new_line)

def append_last_appointment(sms_message, visit):
    value = visit.created.strftime(MESSAGE_REMINDER_DATE_FORMAT)
    line_template = u"Last appointment: %s"
    new_line = line_template.format(value)
    sms_message.add_line(new_line)

def append_biometrics(sms_message, visit):
    """ Appends biometric scorecard based on records whose categories
        are included in RECORD_CATEGORIES_BIOMETRICS
    """
    line_template = u"{displayName}: {value}"
    recordqs = Record.objects.filter(encounter__visit=visit,
                    category__in=RECORD_CATEGORIES_BIOMETRICS).select_related('category')
    for record in recordqs:
        new_line=line_template.format(displayName=record.category.displayName,
                        value=record.value)
        sms_message.add_line(new_line) 

def append_medications(sms_message, end_date, patient):
    """ Queries all of the patients current medications as determined
        by the Medication.edn_date is null or after the 'end_date'
        parameter.
        
        Appends a new line to the message with the medication information
        as:
        name dose dose_unit times per interval interval_unit
    """
    line_template = u"{displayName}: {dose} {dose_unit} {dose_times} per {interval} {interval_unit}"
    medqs = Medication.objects.filter(Q(end_date__isnull=True) | Q(end_date__gt=end_date), 
        encounter__visit__patient=patient).select_related('category','dose_unit', 'interval_unit')
    for med in medqs:
        new_line = line_template.format(
                        displayName=med.category.displayName,
                        dose=med.dose,
                        dose_unit=med.dose_unit.displayName,
                        dose_times=med.times,
                        interval=med.interval,
                        interval_unit=med.interval_unit.displayName)
        sms_message.add_line(new_line)

def calculate_diabetes_status():
    pass

def append_disease_status(sms_message, visit):
    """ Appends control status of patients diagnosed diseases
    """
    pass
    
def append_next_visit_date(sms_message, appointment_date):
    value = appointment_date.strftime(MESSAGE_REMINDER_DATE_FORMAT)
    line_template = u"Next appointment: %s"
    new_line = line_template.format(value)
    sms_message.add_line(new_line)


def get_reminder_record_value(appointment_date):
    """ Generates the text value of the reminder date value to match
        what the client reports. 
    """
    return appointment_date.strftime(RECORD_FOLLOW_UP_DATE_FOMAT)

def get_summary_message(fromSMS, visit, appointment_date):
    message = MESSAGE_SUMMARY_CONTENT
    sms = SMSMessage(fromSMS, toSMS, message)
    # append pt name
    append_patient(sms, visit)
    
    # append last visit
    append_last_appointment(sms,visit)
    
    # append biometrics
    append_biometrics(sms, visit)
    
    # append medications
    append_medications(sms, visit, appointment_date)
    
    # append returned date
    append_next_visit_date(sms, visit)
    return sms

def get_content(fromSMS):
    """ Returns a list of SMS messages to send to patients who have an
        assigned visit on the following day
    """
    # Create a list of messages
    messages = ()
    
    # get tomorrow date object
    now = datetime.datetime.now()
    # Get the time zone offset
    tz_offset = MESSAGE_TIMEZONE.utcoffset(now).total_seconds()/60/60
    tomorrow = now - datetime.timedelta(hours=tz_offset) + datetime.timedelta(days=1)
    record_value = get_reminder_record_value(tomorrow)
    
    # query filter for clinics where patients may get messages
    clinic_qs = get_clinic_qs()
    
    # Get a set of Visit objects where there is a record having the
    # follow up category and value equal to tomorrow and where the visit
    # clinic is one assigned to receive text messages
    visit_qs = get_visits(RECORD_CATEGORY_FOLLOWUP_UUID, record_value, clinic_qs)
    
    # iterate over each of those visits to generate the messages
    for visit in visit_qs:
        # create two arabic instructional mesages
        messages += get_instruction_message_1(fromSMS, visit)
        messages += get_instruction_message_2(fromSMS, visit)
        # create record and medication summary message
        messages += get_summary_message(fromSMS, visit, tomorrow) 
    
    return messages
