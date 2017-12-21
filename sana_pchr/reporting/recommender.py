import datetime
from django.db.models import Q, Count

from sana_pchr.models import *
from sana_pchr.models.medication import *
from .aggregates import *
from .lookups import *
from operator import __iand__, __ior__
import pdb


class RiskLevelCalculator(object):
    """ An object which calculates the number of patients who have a 
        risk level for a condition based on a defined set of 
        calculations
            1. Actively taking a medication to control
            2. Lab test values
            3. Complex calculation defined by calculator
            
        Sub classes should override or add calculate_* methods
    """
    def __init__(self, name, test_category, medication_categories=[], 
                    labtest_categories=[], labtest_levels={}):
        self.name = name
        self.test_category = test_category
        self.medication_categories = medication_categories
        self.labtest_categories = labtest_categories
        self.labtest_levels = labtest_levels
    
    def get_summary( clinic=None, start_date=datetime.date(1900,1,1), end_date=datetime.datetime.now()):
        teQ = Q(created__range=[start_date, end_date])
        if clinic:
            teQ = teQ & Q(clinic=clinic.uuid)
        
        total_encounters = Encounter.objects.filter(teQ)
        te_count = total_encounters.count()
        tp_count = total_encounters.distinct('visit__patient').count()
        
        return [["Total Encounters", te_count],
                ["Total Patients", tp_count]] 
   

    def query_stitch(qlist, operator):
        query = qlist.pop()
        for qs in qlist:
            operator(query, qs)
        return query
 
    def calculate(self, clinic=None, start_date=datetime.date(1900,1,1), end_date=datetime.datetime.now()):
            
        if self.medication_categories:
            teQ = Q(created__range=[start_date, end_date])
            if clinic:
                teQ = teQ & Q(clinic=clinic.uuid)
        
            labtests = self.calculate_labtests(clinic, start_date, end_date)   
            medications = self.calculate_medications(clinic, start_date, end_date)

            return [["Total Encounters", medications['total_encounters']],
                    ["Total Patients", medications['total_patients']],
                    ["Very well controlled", labtests['good_ctrl']],
                    ["Poorly controlled", labtests['poor_ctrl']],
                    ["Lab Tests", labtests['stats']],
                    ["Medications", medications['med_list']]]
        else:
            teQ = Q(created__range=[start_date, end_date])
            if clinic:
                teQ = teQ & Q(encounter__clinic=clinic.uuid)
            testQ = Q(category_id=self.test_category) & teQ
            #This if mostly only for ASCVD. Group patients by ASCVD values
            ret = Test.objects.filter(testQ).values('result').annotate(Count('encounter__visit__patient', distinct=True))
            catObj = TestCategory.objects.get(pk=self.test_category)
            unit = catObj.resultUnits.split('|')
            return [[unit[int(x['result'])], x['encounter__visit__patient__count']] for x in ret]


    def calculate_medications(self, clinic=None, start_date=datetime.date(1900,1,1), end_date=datetime.datetime.now()):
        """
            check if they have any medication.medicationcategory.medicationgroupcategory.uuid 
            that falls onto the values of those dicts
            
        """ 
        startQ = Q(visit__encounter__medication__created__lt=end_date)
        endQ = Q(visit__encounter__medication__end_date__gte=start_date) | Q(visit__encounter__medication__end_date__isnull=True)
        medeQ = startQ & endQ

        if clinic:
            medeQ = medeQ & Q(visit__encounter__clinic=clinic.uuid)
        
        # Compute number of patients on each type of drug
        patlist = Patient.objects.none() 
        data = {}
        for category in self.medication_categories:
            medcatQS = MedicationCategory.objects.filter(group=category)
            medQ = Q(visit__encounter__medication__category__in=medcatQS)
            pats = Patient.objects.filter(medeQ & medQ).distinct()
            patlist = patlist | pats
            catObj = MedicationGroupCategory.objects.get(pk=category)
            data[catObj.displayName] = pats.count()
       
        #Find patients diagnosed, but not on medication
        teQ = Q(visit__created__lt=end_date)
        if clinic:
            teQ = teQ & Q(visit__encounter__clinic=clinic.uuid)
        
        diagQ = Q(visit__encounter__test__category_id=self.test_category)
        diag_pat=Patient.objects.filter(teQ & diagQ).distinct()
        
        patlist = patlist | diag_pat
        patlist = patlist.distinct()
        pat_total = patlist.count()
 

        teQ = Q(created__range=[start_date, end_date])
        if clinic:
            teQ = teQ & Q(clinic=clinic.uuid)
        teQ = teQ & Q(visit__patient__in=patlist)
        encounters = Encounter.objects.filter(teQ).count()
        
        return dict(total_patients=pat_total, total_encounters=encounters, med_list=data)

    def calculate_labtests(self, clinic, start_date, end_date):
        '''
            Compute control and labtest information
        '''
        
        teQ = Q(visit__created__range=[start_date, end_date])
        if clinic:
            teQ = teQ & Q(visit__encounter__clinic=clinic.uuid)  
    
        # Use queries to determine which good (all labtests < first limit)
        # or bad (any labtest higher than last limit)
    
        qpoorctrl = [Q(visit__encounter__test__category_id=x, visit__encounter__test__result__cgt=self.labtest_levels[x][-1]) for x in self.labtest_levels]
        
        qgoodctrl = [Q(visit__encounter__test__category_id=x, visit__encounter__test__result__clt=self.labtest_levels[x][0]) for x in self.labtest_levels]
 
        poorquery = RiskLevelCalculator.query_stitch(qpoorctrl, __ior__)
        goodquery = RiskLevelCalculator.query_stitch(qgoodctrl, __iand__)

        poor_control = Patient.objects.filter(teQ & poorquery).distinct().count()

        good_control = Patient.objects.filter(teQ & goodquery).distinct().count()
    
        #Compute the Min, Max, and Avg of each labtest  
        teQ = Q(created__range=[start_date, end_date])
        if clinic:
            teQ = teQ & Q(encounter__clinic=clinic.uuid)  
     
        stats = {}
        for labtest in self.labtest_categories:
            testQ = teQ & Q(category=labtest)
            vals = Test.objects.filter(testQ).aggregate(max=CastedMax('result'), min=CastedMin('result'), avg=CastedAverage('result'))
            catObj = TestCategory.objects.get(pk=labtest)
            stats[catObj.displayName + " (" + catObj.resultUnits + ")"] = vals
        
        return dict(good_ctrl=good_control, poor_ctrl=poor_control, stats=stats)

    '''    
    def calculate(self, algorithm="complex", clinic=None, start_date=None, end_date=None):
        if not algorithm:
            # TODO raise Exception
            pass
        _func = getattr(self, "calculate_" + algorithm)
        return _func(queryset)
    '''    
# Template for condition dicts
_CONDITION = {
    "name": "",
    "test_category": "",
    "med_categories" :[],
    "labtest_categories" : [],
    "labtest_levels" : {}
    }
    
DYSLIPIDEMIA_CALCULATOR = RiskLevelCalculator(
    "Dyslipidemia Level",
    "5d6a1e16e0324df7a84cc43b65575133",
    medication_categories = [
        "faceec28787c48ce9e4cf3bc40f922a6",
        "cab90da7e4fa4ea1bc39d6e5d7eba26c",
        ],
    labtest_categories = [
        "695164a87e3547d1a4c66020bf2f0a49",
        "ddab66a42a7948109d58d1ba76a0c1b4",
        "a82942e3b50d4ab7900b80f7e2f6b781",
        "0679085bf5af4d06bb0e77dcc26a10d7"
        ],
    labtest_levels = {
        #Lipids
        "695164a87e3547d1a4c66020bf2f0a49":[200, 240],          #chol
        "ddab66a42a7948109d58d1ba76a0c1b4":[100, 130, 160, 190],#ldl
        "a82942e3b50d4ab7900b80f7e2f6b781":[40, 60],            #hdl
        "0679085bf5af4d06bb0e77dcc26a10d7":[150, 200, 500]      #triglycerides
        }
    )
    
HYPERTENSION_CALCULATOR = RiskLevelCalculator(
    "Hypertension Level",
    "2b11c7546c73449681e99b130c6233ec",
    medication_categories = [
        "9293b8b3c713487c953be9dc1df4bbc7",
        "b77208a5fec14830a7b06d6c989c9fbc",
        "a4f38776e1b1430c9129c44982d3b10a",
        "3cbd6bd0987a43358988687f78571640",
        "07de2e12291c47bb9386067457bb1692",
        ],
    labtest_categories = [
        "99daaf48a0c9403caeb964d6a1962b2c",
        "df202805711a4f91b26e6e0b8d923132",
        "91264851f75647b2baa03fda645b9644",
        "148b84bfa5484f39988d01bcc46f0cff"
        ],
    labtest_levels = {
        #Hypertension,  Normal, Pre, S1, S2
        "99daaf48a0c9403caeb964d6a1962b2c":[120, 140, 160],
        "df202805711a4f91b26e6e0b8d923132":[80, 90, 100],
        "91264851f75647b2baa03fda645b9644":[120, 140, 160],
        "148b84bfa5484f39988d01bcc46f0cff":[80, 90, 100],
        }
    )
    
DIABETES_CALCULATOR = RiskLevelCalculator(
    "Diabetes Level",
    "7d03683bcc6b4febb9975ad234b66aef",
    medication_categories = [
        "093fda74d4cf40e384682d9f40dcbb9a",
        "e56a817ffeb2476abbe896b5176880b0",
        "08b7bae9f0c04e2384ce09d33c863b0f"
        ],
    labtest_categories = [
        "d65739b838fe4c9da996d04d8f5b8d8f",
        "b61ea777adf44226b5207e6fa46fcf8e",
        "03392524ec6b4654ba19f3d286f98fbd",
        "88676ce8608a437997b6d228f0e6376c",
        ],
    labtest_levels = {
        #Diabetes, Normal, Pre, Diabetes, Uncontrolled Diabetes
        "d65739b838fe4c9da996d04d8f5b8d8f": [100, 126],     #FBG
        "b61ea777adf44226b5207e6fa46fcf8e":[200, 201],      #RBG
        "03392524ec6b4654ba19f3d286f98fbd":[140, 200],      #OGTT
        "88676ce8608a437997b6d228f0e6376c":[5.7, 6.5, 7],   #HBA1C
        }   
    )

ASCVD_CALCULATOR = RiskLevelCalculator(
    "ASCVD Level",
    "3e1bb876106845dfafccdec0e9a39cc1",
    medication_categories = [],
    labtest_categories = [],
    labtest_levels = {}
    )
