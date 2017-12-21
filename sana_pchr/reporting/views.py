import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from sana_pchr.models import *

EXCLUDE_CLINICS = [
    "Test (Ar)", 
    "Test (En)"
]
# Helper functions called by views.py 
# to calculate the data provided in the dashboard

def _get_diagnosis_by_medication(clinic=None, start_date=datetime.date(1900,1,1), end_date=datetime.datetime.now()):
    
    data = {}
    # 1 = dyslipidemia, 2 = hypertension, 3 = diabetes
    med_categories = {
        "Dyslipidemia Level" : [
            "faceec28787c48ce9e4cf3bc40f922a6",
            "cab90da7e4fa4ea1bc39d6e5d7eba26c",
            ],
        "Hypertension Level" : [
            "9293b8b3c713487c953be9dc1df4bbc7",
            "b77208a5fec14830a7b06d6c989c9fbc",
            "a4f38776e1b1430c9129c44982d3b10a",
            "3cbd6bd0987a43358988687f78571640",
            "07de2e12291c47bb9386067457bb1692",
            ],
        "Diabetes Level" : [
            "093fda74d4cf40e384682d9f40dcbb9a",
            "e56a817ffeb2476abbe896b5176880b0",
            "08b7bae9f0c04e2384ce09d33c863b0f"
            ],
        "ASCVD Level" : [
            ]
        }
    
    teQ = Q(created__range=[start_date, end_date])
    if clinic:
        teQ = teQ & Q(clinic=clinic.uuid)
    total_encounters = Encounter.objects.filter(teQ)
    te_count = total_encounters.count()
    tp_count = total_encounters.distinct('visit__patient').count()
    for name, categories in med_categories.items():
        if len(categories) == 0:
            data[name] = {
                "Number of Encounters": 0,
                "Number of Patients": 0,
                "Well Managed": "NA"
            }
        else:
            medgroupcatQS = MedicationGroupCategory.objects.filter(uuid__in=categories)
            medcatQS = MedicationCategory.objects.filter(group__in=medgroupcatQS)
            medQ = Q(category__in=medcatQS) & Q(encounter__created__range=[start_date, end_date])
            if clinic:
                medQ = medQ & Q(encounter__clinic=clinic.uuid) 
            medQS = Medication.objects.filter(medQ)
            eqs = medQS.distinct('encounter').values_list('encounter', flat=True)
            encounters = Encounter.objects.filter(uuid__in=eqs)
            vqs = encounters.values_list('visit', flat=True)
            visits = Visit.objects.filter(uuid__in=vqs)
            pqs = visits.distinct('patient').values_list('patient', flat=True)
            
            data[name] = {
                    "Number of Encounters": len(eqs),
                    "Number of Patients": len(pqs),
                    "Well Managed": str(len(pqs))  + "/" + str(tp_count)
            }
    return data

def _get_patients_from_encounters(encounters):
    """Input list of encounters, return a list of all 
    the patients within those encounters"""
    patients = set()
    for enc in encounters:
        patients.add(enc.visit.patient.uuid)
    return patients

def _get_encounter_data(clinics):
    """Create a json containing number of encounters per clinic and for all clinics
     filtered by occurring in past day, week, month, year, and all"""
    # TODO: provide kwarg that allows user to pass in custom date range and include 
    # encounters and patients over that date range in the final returned json 
    # by including it in time intervals

    now = datetime.datetime.now()
    # Provide statistics for 1 day, 1 month, 1 year, and all-time
    time_intervals = {
        "day": now - datetime.timedelta(days=1), 
        "month": now - datetime.timedelta(days=30),
        "year": now - datetime.timedelta(days=365),
        "all-time": None
    }

    json_resp = {}

    # Clinic specific queries
    for clinic in clinics:
        json_resp[clinic.name] = {}
        for name, cutoff in time_intervals.items():
            if name == "all-time":
                encounters = Encounter.objects.filter(clinic=clinic.uuid)
            else:
                encounters = (
                    Encounter.objects.filter(clinic=clinic.uuid).
                    filter(created__gt=cutoff).all()
                )
            patients = _get_patients_from_encounters(encounters)

            json_resp[clinic.name][name] = {
                "patients": len(patients),
                "encounters": len(encounters)
            }

    # Aggregate Queries across all clinics
    json_resp["[All Clinics]"] = {}
    for name, cutoff in time_intervals.items():
        if name == "all-time":
            encounters = Encounter.objects.all()
        else:
            encounters = Encounter.objects.filter(created__gt=cutoff).all()
        patients = _get_patients_from_encounters(encounters)

        json_resp["[All Clinics]"][name] = {
            "patients": len(patients),
            "encounters": len(encounters)
        }

    return json_resp

def _get_diagnosis_info(clinics):
    """Get per-clinic data on various diagnoses"""

    # Tests to display on reporting page (test category UUIDs)
    test_categories = {
        "Diabetes Level": "7d03683bcc6b4febb9975ad234b66aef",
        "Hypertension Level": "2b11c7546c73449681e99b130c6233ec",
        "Dyslipidemia Level": "5d6a1e16e0324df7a84cc43b65575133",
        "ASCVD Level":  "3e1bb876106845dfafccdec0e9a39cc1"
    }

    # 1 = dyslipidemia, 2 = hypertension, 3 = diabetes
    med_categories = {
        "faceec28787c48ce9e4cf3bc40f922a6":"1",
        "cab90da7e4fa4ea1bc39d6e5d7eba26c":"1",
        "9293b8b3c713487c953be9dc1df4bbc7":"2",
        "b77208a5fec14830a7b06d6c989c9fbc":"2",
        "a4f38776e1b1430c9129c44982d3b10a":"2",
        "3cbd6bd0987a43358988687f78571640":"2",
        "07de2e12291c47bb9386067457bb1692":"2",
        "093fda74d4cf40e384682d9f40dcbb9a":"3",
        "e56a817ffeb2476abbe896b5176880b0":"3",
        "08b7bae9f0c04e2384ce09d33c863b0f":"3"
    }

    labtest_categories = {
        "d65739b838fe4c9da996d04d8f5b8d8f":"3",
        "b61ea777adf44226b5207e6fa46fcf8e":"3",
        "03392524ec6b4654ba19f3d286f98fbd":"3",
        "88676ce8608a437997b6d228f0e6376c":"3",
        "99daaf48a0c9403caeb964d6a1962b2c":"2",
        "df202805711a4f91b26e6e0b8d923132":"2",
        "91264851f75647b2baa03fda645b9644":"2",
        "148b84bfa5484f39988d01bcc46f0cff":"2",
        "695164a87e3547d1a4c66020bf2f0a49":"1",
        "ddab66a42a7948109d58d1ba76a0c1b4":"1",
        "a82942e3b50d4ab7900b80f7e2f6b781":"1",
        "0679085bf5af4d06bb0e77dcc26a10d7":"1"
    }

    labtest_levels = {
                #Diabetes, Normal, Pre, Diabetes, Uncontrolled Diabetes
        "d65739b838fe4c9da996d04d8f5b8d8f":[100, 126],
        #FBG
        "b61ea777adf44226b5207e6fa46fcf8e":[200, 201],
        #RBG
        "03392524ec6b4654ba19f3d286f98fbd":[140, 200],
        #OGTT
        "88676ce8608a437997b6d228f0e6376c":[5.7, 6.5, 7],
        #HBA1C

        #Hypertension,  Normal, Pre, S1, S2
        "99daaf48a0c9403caeb964d6a1962b2c":[120, 140, 160],
        "df202805711a4f91b26e6e0b8d923132":[80, 90, 100],
        "91264851f75647b2baa03fda645b9644":[120, 140, 160],
        "148b84bfa5484f39988d01bcc46f0cff":[80, 90, 100],

        #Lipids
        "695164a87e3547d1a4c66020bf2f0a49":[200, 240],
        #chol
        "ddab66a42a7948109d58d1ba76a0c1b4":[100, 130, 160, 190],
        #ldl
        "a82942e3b50d4ab7900b80f7e2f6b781":[40, 60],
        #hdl
        "0679085bf5af4d06bb0e77dcc26a10d7":[150, 200, 500]
        #triglycerides
    }

    json_resp = {}

    # Per-clinic stats
    for clinic in clinics:
        json_resp[clinic.name] = _get_diagnosis_by_medication(clinic=clinic)
    # Aggregate Stats
    json_resp["[All Clinics]"] = _get_diagnosis_by_medication()
    
    return json_resp


@login_required
def dashboard(request):
    clinics = Clinic.objects.all().order_by('name').exclude(name__in=EXCLUDE_CLINICS)
        
    clinic_usage = _get_encounter_data(clinics)
    tests = _get_diagnosis_info(clinics)

    context = {
        "clinics": clinics, 
        "usage": clinic_usage,
        "tests": tests
    }
    return render(request, 'reporting/index.html', context)






