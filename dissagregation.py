import sys, csv,os
import numpy as np
import pandas as pd
from os import environ,path
sys.path.append('config')
from config import config
from connect import connect
from ROIFunctions.common_functions import getDataDB,generateCsv,insertParameter

# Generación de los csv pertinentes para el algoritmo de dissagregation
def DataCSVDis(path_data_in, catchment,studycase):
    genCSVInvest(path_data_in, catchment,studycase, '__wp_dissagregation_invest','01-INPUTS_InVEST.csv')
    genCSVNBS(path_data_in, studycase, '__wp_dissagregation_nbs_first', '__wp_dissagregation_nbs_second','01-INPUTS_NBS.csv',catchment)
    genCSVTime(path_data_in, studycase, '__wp_dissagregation_time','01-INPUTS_Time.csv')

# genera el archivo Invest 
# header = cabecera del archivo
# results = datos que se llaman de la base de datos mediante una función
def genCSVInvest(path_data_in, catchment,studycase, function_id, csv_in):
    header=["Scenario-InVEST","AWY (m3)","Wsed (Ton)","WN (Kg)","WP (kg)","BF (m3)","WC (Ton)"]
    results = getDataDB( [catchment, studycase], function_id )
    pathcsv = path.join( path_data_in, csv_in)
    generateCsv( header, results, pathcsv)

# genera el archivo csv de NBS
def genCSVNBS(path_data_in, studycase, function_id1, function_id2, csv_in, catchment):
    header=["NBS-Name",	"Time-Max-Benefit",	"Benefit-t0"]
    results1 = getDataDB( [studycase], function_id1)
    results2 = getDataDB( [studycase, catchment], function_id2)

    # Se ordenan los resultados obtenidos en la DB
    # para poder generar la estructura solicitada en el csv
    results1tot=[]
    for first in results1:
        order = list(first)
        for val in results2:
            if (first[3]==val[0]):
                order.append(val[2])

        order.pop(3)
        results1tot.append(order)

    tot=len(results2)/len(results1)

    # Se adicionan las otras cabeceras al archivo
    # A-n (ha)
    for i in range(int(tot)):
        header.append('A-'+str(i+1)+' (ha)')
    pathcsv = path.join( path_data_in, csv_in)    
    generateCsv( header, results1tot, pathcsv)

# genera el archivo csv de Time
def genCSVTime(path_data_in, studycase, function_id, csv_in):
    header=["Time"]
    results = getDataDB( [studycase], function_id)
    pathcsv = path.join( path_data_in, csv_in)
    generateCsv( header, results, pathcsv)

def DisaggregationOut(path_data_in,catchment,studycase):

    bau_df = pd.read_csv(os.path.join(path_data_in,'02-OUTPUTS_BaU.csv'))
    nbs_df = pd.read_csv(os.path.join(path_data_in,'02-OUTPUTS_NBS.csv'))
    DisaggregationOutInsert(bau_df,'BAU',catchment,studycase)
    DisaggregationOutInsert(nbs_df,'NBS',catchment,studycase)
    
def DisaggregationOutInsert(df,stage,catchment,studycase):
    Time   = df['Time'].values
    Awy    = df['AWY (m3)'].values
    Wsed   = df['Wsed (Ton)'].values
    Wn     = df['WN (Kg)'].values
    Wp     = df['WP (kg)'].values
    Bf     = df['BF (m3)'].values
    Wc     = df['WC (Ton)'].values

    for idx,item in enumerate(df['Time']):
        args= [int(Time[idx]),stage,int(catchment),int(studycase),Awy[idx], Wsed[idx], Wn[idx], Wp[idx], Bf[idx], Wc[idx]]
        insertParameter('__wp_insert_disaggregation', args)

