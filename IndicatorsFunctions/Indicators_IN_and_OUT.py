import os,glob,re
import numpy as np
import pandas as pd
from datetime import date
from ROIFunctions.common_functions import insertParameter,generateCsv
from os import environ, path
from connect import connect
import constants

OUT_DIR = 'out'
DISAGGREGATION_DIR = '07-DISAGGREGATION'
INDICATORS = 'INDICATORS'

def IndicatorsIn(path_data):
    # try:
    dirs = os.listdir(path_data)
    dirs.sort()
    dirs2=[]
    for dir in dirs:
        if 'WI' in dir:
            dirs2.append(dir)

    for idx,dir in enumerate(dirs2):
            id_intake = re.findall(r"([0-9]+)$", dir)
            dir_in = int(id_intake[0])
            BaU = pd.read_csv(path.join( path_data, dir, OUT_DIR,DISAGGREGATION_DIR, '02-OUTPUTS_BaU.csv'))
            NBS = pd.read_csv(path.join( path_data, dir, OUT_DIR,DISAGGREGATION_DIR, '02-OUTPUTS_NBS.csv'))
            path_BaU = path.join(path_data, INDICATORS, str(idx+1)+'-INPUTS_BaU.csv')
            path_NBS = path.join(path_data, INDICATORS, str(idx+1)+'-INPUTS_NBS.csv')
            generateCsv(list(BaU.columns), BaU.values.tolist(), path_BaU)
            generateCsv(list(NBS.columns), NBS.values.tolist(), path_NBS)
    # except Exception as e:
    #     return print(e.args)

def IndicatorsSaveDB(path_data,user_id,study_case_id,date):
    INTAKE_IND = 'Intake_ind'
    INTAKE_TOT = 'Total_ind'
    dirs = os.listdir(path_data)
    ids=[]
    for idx,dir in enumerate(dirs):
        if 'WI' in dir:
            id_intake = re.findall(r"([0-9]+)$", dir)
            ids.append(int(id_intake[0]))

    # List Basin
    ListBasin        = glob.glob(os.path.join(path_data,INDICATORS, '*OUTPUTS*'))
    n = int(len(ListBasin)/2)
    for k in range(n-1):
        time_serie   = pd.read_csv(os.path.join(path_data,INDICATORS, str(k+1) + '-OUTPUTS_Indicators_TimeSeries.csv'))
        max_indica   = pd.read_csv(os.path.join(path_data,INDICATORS, str(k+1) + '-OUTPUTS_Max_Indicators.csv'))

        time_in      = time_serie['Time'].values.tolist()
        awy_in       = time_serie['AWY (m3)'].values.tolist()
        wn_in        = time_serie['WN (Kg)'].values.tolist()
        wp_in        = time_serie['WP (kg)'].values.tolist()
        wsed_in      = time_serie['Wsed (Ton)'].values.tolist()
        bf_in        = time_serie['BF (m3)'].values.tolist()
        wc_in        = time_serie['WC (Ton)'].values.tolist()

        args =[time_in,awy_in,wn_in,wp_in,wsed_in,bf_in,wc_in]
        final = pd.DataFrame(data=np.array(args))

        for label,series in final.items():
            val = series.values
            args_in =[int(val[0]),str(INTAKE_IND),str(path_data),date,val[1],val[2],val[3],val[4],val[5],val[6],ids[k],study_case_id,user_id]
            insertParameter('__wp_indicators_insert',args_in)


    time = pd.read_csv(path.join( path_data, INDICATORS, 'OUTPUTS-Indicators_TimeSeries_Total.csv'))
    NBS = pd.read_csv(path.join( path_data, INDICATORS, 'OUTPUTS-Max_Indicators_Total.csv'))

    time_in      = time['Time'].values.tolist()
    awy_in       = time['AWY (m3)'].values.tolist()
    wn_in        = time['WN (Kg)'].values.tolist()
    wp_in        = time['WP (kg)'].values.tolist()
    wsed_in      = time['Wsed (Ton)'].values.tolist()
    bf_in        = time['BF (m3)'].values.tolist()
    wc_in        = time['WC (Ton)'].values.tolist()

    args =[time_in,awy_in,wn_in,wp_in,wsed_in,bf_in,wc_in]
    final = pd.DataFrame(data=np.array(args))

    for label,series in final.items():
        val = series.values
        args_in =[int(val[0]),INTAKE_TOT,path_data,date,val[1],val[2],val[3],val[4],val[5],val[6],int(-1),study_case_id,user_id]
        insertParameter('__wp_indicators_insert',args_in)