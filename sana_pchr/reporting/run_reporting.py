from sana_pchr.reporting.recommender import *
from datetime import timedelta, date
from dateutil import rrule
import csv

calcs = [DIABETES_CALCULATOR, HYPERTENSION_CALCULATOR, DYSLIPIDEMIA_CALCULATOR]
clinics = [clinic for clinic in Clinic.objects.all() if "Test" not in clinic.name ]

start_date = date(2016,2,14)
end_date = date(2016,10,30)

#Parses the JSON-like format into outputs that can be output itno a CSV file
def parse_out(y, prefix):
    out = {}

    #recursive function that can take care of dicts or lists
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    for a in y:
        flatten(a[1], prefix + '_' + a[0] + '_')

    return out

#runs the analysis
def run():
    for clinic in clinics:
        last_date = date(2016,2,7)
        with open(clinic.name + ".csv", mode="w") as outfile:
            row = 1
            for dt in rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date):
                summary_out = parse_out(RiskLevelCalculator.get_summary(clinic, last_date, dt), 'All')
                calc_outs = [parse_out(calc.calculate(clinic, last_date, dt),calc.name) for calc in calcs]
                combd = {}
                for calc_out in calc_outs:
                    combd.update(calc_out)
                combd.update(summary_out)

                if row == 1:
                    fields = ["week_starting" , 'ASCVD Level_<10%', 'ASCVD Level_10-20%', 'ASCVD Level_20-30%', 'ASCVD Level_30-40%','ASCVD Level_>40%'] + sorted(combd)
                    writer = csv.DictWriter(outfile, fieldnames=fields)
                    writer.writeheader()
                    row = 2
                #Need this workaround with ASCVD calc b/c grouping is only by ones present, need all for header
                combd.update(parse_out(ASCVD_CALCULATOR.calculate(clinic, last_date, dt), 'ASCVD Level'))
                combd.update({'week_starting': last_date.strftime("%Y-%m-%d")})
                writer.writerow(combd)
                last_date = dt
