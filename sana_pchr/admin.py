from django.contrib import admin
from sana_pchr.models import Device, Physician, Patient, Visit, Clinic, Encounter, Patient_Physician, Record, Test, \
    VisitCategory, EncounterCategory, RecordCategory, TestCategory, Clinic_Physician
from sana_pchr.models.medication import *
from sana_pchr.models.event import Event
from sana_pchr.forms.admin.physician import PhysicianForm
from sana_pchr.forms.admin.patient import PatientForm
from sana_pchr.forms.admin.app import AppForm


class SynchronizedAdmin(admin.ModelAdmin):
    readonly_fields = ["uuid", "synchronized"]


class PatientPhysicianInline(admin.TabularInline):
    model = Patient_Physician
    extra = 1


class ClinicPhysicianInline(admin.TabularInline):
    model = Clinic_Physician
    extra = 1


class DeviceAdmin(SynchronizedAdmin):
    readonly_fields = SynchronizedAdmin.readonly_fields + ['token']
    list_display = ['clinic', 'name', 'deviceMAC', 'currentVersion', 'lastSynchronized']

admin.site.register(Device, DeviceAdmin)


class PhysicianAdmin(SynchronizedAdmin):
    list_display = ['firstName', 'lastName', 'email', 'phone']
    filter_horizontal = ["clinics"]
    form = PhysicianForm

admin.site.register(Physician, PhysicianAdmin)


class ClinicAdmin(SynchronizedAdmin):
    inlines = (ClinicPhysicianInline,)
    filter_horizontal = ["physicians"]

admin.site.register(Clinic, ClinicAdmin)


class VisitAdmin(SynchronizedAdmin):
    raw_id_fields = ["patient"]

admin.site.register(Visit, VisitAdmin)


class EncounterAdmin(SynchronizedAdmin):
    raw_id_fields = ["physician", "device", "clinic"]

admin.site.register(Encounter, EncounterAdmin)


class PatientAdmin(SynchronizedAdmin):
    list_display = ["firstName", "lastName", "UNHCR", "birthYear", "birthCity", "gender"]
    inlines = (PatientPhysicianInline,)
    filter_horizontal = ["physicians"]
    form = PatientForm


admin.site.register(Patient, PatientAdmin)


class EncounterRelatedAdmin(SynchronizedAdmin):
    raw_id_fields = ["encounter"]


class EventAdmin(admin.ModelAdmin):
    list_display = [
        "device", "clinic", "status", "code", "message",
    ]
    list_filter = [
        "device", "clinic", "status", "code"
    ]
admin.site.register(Event, EventAdmin)

admin.site.register(Record, EncounterRelatedAdmin)
admin.site.register(Test, EncounterRelatedAdmin)

admin.site.register(VisitCategory, SynchronizedAdmin)
admin.site.register(EncounterCategory, SynchronizedAdmin)

class TestCategoryAdmin(SynchronizedAdmin):
    list_display = ['displayName', 'displayNameAr', 'resultUnits', 'resultUnitsAr', 'priority']

admin.site.register(TestCategory, TestCategoryAdmin)
admin.site.register(RecordCategory, SynchronizedAdmin)

admin.site.register(Medication, SynchronizedAdmin)
admin.site.register(MedicationCategory, SynchronizedAdmin)
admin.site.register(MedicationGroupCategory, SynchronizedAdmin)
admin.site.register(DoseUnitCategory, SynchronizedAdmin)
admin.site.register(IntervalUnitCategory, SynchronizedAdmin)
