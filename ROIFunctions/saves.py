import numpy as np
import pandas as pd
import datetime
from ROIFunctions.common_functions import insertParameter,getDataDB

def Save_roi( anotherroute, studycase, type_in, ejecution, idx ):
    # get data from csv
    save_zer = pd.read_csv(anotherroute+f'/{idx}.0_{ejecution}_Saves.csv')
    save_one = pd.read_csv(anotherroute+f'/{idx}.1_{ejecution}_Saves.csv')
    save_two = pd.read_csv(anotherroute+f'/{idx}.2_{ejecution}_Saves.csv')
    save_tre = pd.read_csv(anotherroute+f'/{idx}.3_{ejecution}_Saves.csv')

    value=[]
    for col, serie in save_zer.iterrows():
        value.append(serie.values[1:])

    vpn_min_save=[]
    for col, serie in save_one.iterrows():
        vpn_min_save.append(serie.values[1:])

    vpm_max_save=[]
    for col, serie in save_tre.iterrows():
        vpm_max_save.append(serie.values[1:])

    vpn_med_save=[]
    serie_time=[]
    for col, serie in save_two.iterrows():
        vpn_med_save.append(serie.values[1:])
        serie_time.append(serie.index.values[1:])

    save_id_out=[]
    for save in save_zer['Process']:
        if(save == 'NoData'):
            save_id_out=[0 for var in range(serie_time[0].size)]
        else:
            list_in = [save for var in range(serie_time[0].size)]
            save_id_out+=list_in


    today = datetime.date.today()
    date = f'{today.year}-{today.month}-{today.day}'
    vpn_min_save_out = np.array(vpn_min_save).flatten()
    vpm_max_save_out = np.array(vpm_max_save).flatten()
    vpn_med_save_out = np.array(vpn_med_save).flatten()
    serie_time_out = np.array(serie_time).flatten()
    value_out = np.array(value).flatten()
    currency = getDataDB([studycase],'__wp_roi_tc_exchange_rate_exception')
    currency= list(currency[0])

    # Generate dataframe with all data to insert
    final = pd.DataFrame(data=np.array([serie_time_out,value_out,save_id_out,vpn_min_save_out,vpm_max_save_out,vpn_med_save_out]))

    for label,series in final.items():
        val = series.values
        args=[ currency[0], val[0], val[1], val[2], studycase, date, type_in, val[3], val[4], val[5] ]
        insertParameter( '__wp_roi_insert_save', args )