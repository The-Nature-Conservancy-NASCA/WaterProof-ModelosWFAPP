import numpy as np
import pandas as pd
import datetime
from ROIFunctions.common_functions import insertParameter,getDataDB

def Sens_roi( anotherroute, studycase ):
    # get data from csv
    sensivity = pd.read_csv(anotherroute+'/12_ROI_Sensitivity.csv')
    npv_csv = pd.read_csv(anotherroute+'/13_NPV.csv')

    today = datetime.date.today()
    date = f'{today.year}-{today.month}-{today.day}'
    currency = getDataDB([studycase],'__wp_roi_tc_exchange_rate_exception')
    currency = list(currency[0])

    argssensi=[
        currency[0], 
        sensivity['Total'].values[0],
        sensivity['TD_Min'].values[0],
        sensivity['TD_Max'].values[0],
        sensivity['TD_Mean'].values[0],
        studycase,
        date
    ]
    argsnpv=[
        currency[0], 
        npv_csv['Implementation'].values[0],
        npv_csv['Maintenance'].values[0],
        npv_csv['Oportunity'].values[0],
        npv_csv['Transaction'].values[0],
        npv_csv['Platform'].values[0],
        npv_csv['Benefit'].values[0],
        npv_csv['Total'].values[0],
        studycase,
        date
    ]
    insertParameter( '__wp_roi_insert_sensitivity', argssensi )
    insertParameter( '__wp_roi_insert_vpn', argsnpv )