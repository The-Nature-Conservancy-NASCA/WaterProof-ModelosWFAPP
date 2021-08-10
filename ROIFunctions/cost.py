import numpy as np
import pandas as pd
import datetime
from ROIFunctions.common_functions import insertParameter,getDataDB

def Cost_roi( anotherroute, studycase, type_in, ejecution, idx ):
    # get data from csv
    cost_zer = pd.read_csv(anotherroute+f'/{idx}.0_{ejecution}_Costs.csv')
    cost_one = pd.read_csv(anotherroute+f'/{idx}.1_{ejecution}_Costs.csv')
    cost_two = pd.read_csv(anotherroute+f'/{idx}.2_{ejecution}_Costs.csv')
    cost_tre = pd.read_csv(anotherroute+f'/{idx}.3_{ejecution}_Costs.csv')

    cost_id=[]
    value=[]
    vpn_min_cost=[]
    vpm_max_cost=[]
    vpn_med_cost=[]
    for col in cost_zer:
        serie_time = cost_zer['Time']
        cost_id.append(cost_zer[col].name)
        value.append(cost_zer[col])
        vpn_min_cost.append(cost_one[col])
        vpn_med_cost.append(cost_two[col])
        vpm_max_cost.append(cost_tre[col])

    # Delete row time from the matrix
    cost_id.pop(0)
    value.pop(0)
    vpn_min_cost.pop(0)
    vpm_max_cost.pop(0)
    vpn_med_cost.pop(0)

    cost_id_out=[]
    serie_time_out=[]
    for cost in cost_id:
        list_in = [cost for var in range(serie_time.size)]
        cost_id_out+=list_in
        serie_time_out.append(serie_time)
    today = datetime.date.today()
    date = f'{today.year}-{today.month}-{today.day}'
    vpn_min_cost_out = np.array(vpn_min_cost).flatten()
    vpm_max_cost_out = np.array(vpm_max_cost).flatten()
    vpn_med_cost_out = np.array(vpn_med_cost).flatten()
    serie_time_out = np.array(serie_time_out).flatten()
    value_out = np.array(value).flatten()
    currency = getDataDB([studycase],'__wp_roi_tc_exchange_rate_exception')
    currency= list(currency[0])

    # Generate dataframe with all data to insert
    final = pd.DataFrame(data=np.array([serie_time_out,value_out,cost_id_out,vpn_min_cost_out,vpm_max_cost_out,vpn_med_cost_out]))

    for label,series in final.items():
        val = series.values
        args = [currency[0], int(val[0]), val[1], studycase, val[2], date, type_in, val[3], val[4], val[5]]
        insertParameter( '__wp_roi_insert_cost', args )
