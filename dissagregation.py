import sys, csv
import numpy as np
import pandas as pd
from os import environ,path
sys.path.append('config')
from config import config
from connect import connect
from getDataWB import getDataDB,generateCsv



ruta = environ["PATH_FILES"]


in_invest = '01-INPUTS_InVEST.csv'
in_nbs    = '01-INPUTS_NBS.csv'
in_time   = '01-INPUTS_Time.csv'

def DataCSVDis(type,catchment,studycase):
    genCSVInvest(catchment,studycase, '__wp_dissagregation_invest',in_invest)
    genCSVNBS(studycase, '__wp_dissagregation_nbs_first', '__wp_dissagregation_nbs_second',in_nbs)
    genCSVTime(studycase, '__wp_dissagregation_time',in_time)


def genCSVInvest(catchment,studycase, function_id, csv_in):
    header=["Scenario-InVEST","AWY (m3)","Wsed (Ton)","WN (Kg)","WP (kg)","BF (m3)","WC (Ton)"]
    results = getDataDBInVEST( catchment, studycase, function_id )
    pathcsv= path.join( ruta, "salidas", "disaggregation", "INPUTS", csv_in )
    generateCsv( header, results, pathcsv )

def genCSVNBS(studycase, function_id1, function_id2, csv_in):
    header=["NBS-Name",	"Time-Max-Benefit",	"Benefit-t0"]
    results1 = getDataDB( studycase, function_id1 )
    results2 = getDataDB( studycase, function_id2 )

    results1tot=[]
    for first in results1:
        order = list(first)
        for val in results2:
            if (first[3]==val[0]):
                order.append(val[2])

        order.pop(3)
        results1tot.append(order)

    tot=len(results2)/len(results1)
    
    for i in range(int(tot)):
        header.append('A-'+str(i+1)+' (ha)')
        
    pathcsv= path.join( ruta, "salidas", "disaggregation", "INPUTS", csv_in )
    generateCsv( header, results1tot, pathcsv )

def genCSVTime(studycase, function_id, csv_in):
    header=["Time"]
    results = getDataDB( studycase, function_id )
    pathcsv= path.join( ruta, "salidas", "disaggregation", "INPUTS", csv_in )
    generateCsv( header, results, pathcsv )

def getDataDBInVEST( catchment, studycase,  funcion_db ):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc(funcion_db,[catchment,studycase])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    if (listResult ==[]):
        raise Exception(f'Sin datos para el id: {id}')

    return listResult
