import numpy as np
import pandas as pd
import datetime
from ROIFunctions.common_functions import insertParameter,getDataDB

def Carb_roi( anotherroute, studycase ):
    carb_zer = pd.read_csv(anotherroute+f'/8.0_Carbons_Saves.csv')
    carb_one = pd.read_csv(anotherroute+f'/8.1_Carbons_Saves.csv')
    carb_two = pd.read_csv(anotherroute+f'/8.2_Carbons_Saves.csv')
    carb_tre = pd.read_csv(anotherroute+f'/8.3_Carbons_Saves.csv')

    serie_time   = carb_zer.index
    value        = carb_zer['Carbons'].values
    vpn_min_carb = carb_one['Carbons'].values
    vpn_med_carb = carb_two['Carbons'].values
    vpm_max_carb = carb_tre['Carbons'].values

    today = datetime.date.today()
    date = f'{today.year}-{today.month}-{today.day}'
    currency = getDataDB([studycase],'__wp_roi_tc_exchange_rate_exception')
    currency= list(currency[0])


# Generate dataframe with all data to insert
    final = pd.DataFrame(data=np.array([serie_time,value,vpn_min_carb,vpm_max_carb,vpn_med_carb]))

    for label,series in final.items():
        val = series.values
        args=[ currency[0], int(val[0])+1, val[1], int(-1), studycase, date, 'CARBONO', val[2], val[3], val[4] ]
        insertParameter( '__wp_roi_insert_save', args )
