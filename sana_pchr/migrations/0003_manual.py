# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import migrations


def forwards_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Clinic_Physician = apps.get_model("sana_pchr", "Clinic_Physician")
    Patient_Physician = apps.get_model("sana_pchr", "Patient_Physician")

    Encounter = apps.get_model("sana_pchr", "Encounter")
    encounters = Encounter.objects.using(db_alias).all().select_related('clinic', 'patient', 'physician')
    # Find and populate missing connections
    for encounter in encounters:
        clinic = encounter.clinic
        physician = encounter.physician
        if physician not in clinic.physicians.all():
            Clinic_Physician(clinic=clinic, physician=physician).save()
        patient = encounter.visit.patient
        if physician not in patient.physicians.all():
            Patient_Physician(patient=patient, physician=physician).save()

    remove_duplicates_set_uuid(Clinic_Physician, 'clinic', 'physician', db_alias)
    remove_duplicates_set_uuid(Patient_Physician, 'patient', 'physician', db_alias)


# Remove duplicates and concatenate UUIDS
def remove_duplicates_set_uuid(field, fk1, fk2, db):
    rows = field.objects.using(db).all().order_by(fk1, fk2)
    last_val = ('Not a value', 'Not a value')
    for row in rows:

        cur_val = (getattr(row, fk1).uuid, getattr(row, fk2).uuid)
        if cur_val == last_val:
            field.objects.using(db).get(uuid=row.uuid).delete()
        else:
            old_uuid = row.uuid
            field.objects.using(db).get(uuid=old_uuid).delete()
            row.uuid = cur_val[0][0:15] + cur_val[1][0:15]
            row.save()
            last_val = cur_val


# Generate new UUIDs
def shorten_uuid(field, db):
    rows = field.objects.using(db).all()
    for row in rows:
        row.delete()
        row.uuid = uuid.uuid4().hex
        row.save()


def reverse_func(apps, schema_editor):
    Clinic_Physician = apps.get_model("sana_pchr", "Clinic_Physician")
    Patient_Physician = apps.get_model("sana_pchr", "Patient_Physician")
    db_alias = schema_editor.connection.alias
    shorten_uuid(Clinic_Physician, db_alias)
    shorten_uuid(Patient_Physician, db_alias)


class Migration(migrations.Migration):
    dependencies = [
        ('sana_pchr', '0002_auto_20160106_0638'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_code=reverse_func)
    ]
