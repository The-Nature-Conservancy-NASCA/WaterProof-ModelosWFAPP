import os
import numpy as np
import pandas as pd
from datetime import date
from ROIFunctions.common_functions import getDataDB,generateCsv
from os import environ, path
from connect import connect
import constants

ruta = environ["PATH_FILES"]
ROI = 'ROI' 
IN = 'in'
OUT = 'out'
# Generación de los csv pertinentes para el algoritmo de ROI

def DataCSVRoi(user_id, studycase, date, path_data):
    genCSVCost(studycase, '__wp_roi_cost', 'intake','NBS', '1_CostFunction_NBS_Cap.csv', path_data)
    genCSVCost(studycase, '__wp_roi_cost', 'intake','BAU', '2_CostFunction_BaU_Cap.csv', path_data)
    genCSVCost(studycase, '__wp_roi_cost', 'PTAP','NBS', '3_CostFunction_NBS_PTAP.csv', path_data)
    genCSVCost(studycase, '__wp_roi_cost', 'PTAP','BAU', '4_CostFunction_BaU_PTAP.csv', path_data)
    genCSVNBS_Cost(studycase, '__wp_roi_nbs_cost', '5_NBS_Cost.csv', path_data)
    genCSVPort_NBS(studycase, '__wp_dissagregation_nbs_first','__wp_roi_nbs_porfolio', '6_Porfolio_NBS.csv', path_data)
    genCSVFin_Par(studycase, '__wp_roi_financial_parameters_first','__wp_roi_financial_parameters_second', '7_Financial_Parmeters.csv', path_data)
    genCSVTime(studycase, '__wp_roi_time', '8_Time.csv', path_data)
    genCSVCO2(studycase, '02-OUTPUTS_BaU.csv', '9-CO2_BaU.csv', date, user_id, path_data)
    genCSVCO2(studycase, '02-OUTPUTS_NBS.csv', '10-CO2_NBS.csv', date, user_id, path_data)

# 1-4 Genera el archivo csv de costos para NBS-BAU para Intake-PTAP

def genCSVCost(studycase, function_id, types, stage, csv_in, path_data):
    header = ["Process", "Cost_Function"]
    result = getDataDB([studycase, types, stage], function_id)

    if(result != []):
        # encontrar los id de las funciones ya que no se repiten
        elements_id = []
        for res in result:
            elements_id.append(res[3])
        elements_id = list(set(elements_id))

        results1tot = []
        header1 = []
        for cab in elements_id:
            cost_function = []
            opt = []
            id_elem = []
            for res in result:
                res = list(res)
                if(cab == res[3]):
                    header1.append(res[1])
                    id_elem.append(res[0])
                    cost_function.append(res[3])
                    opt.append(res[2])
            cost_function = list(set(cost_function))
            opt.insert(0, cost_function[0])
            opt.insert(0, id_elem[0])
            results1tot.append(opt)
        header1 = list(set(header1))
        header += header1
    else:
        header.append(0)
        results1tot = [[0,0,0]]

    pathcsv = path.join(path_data, ROI, IN, csv_in)
    generateCsv(header, results1tot, pathcsv)

# 5 Genera el archivo csv de NBS_Cost

def genCSVNBS_Cost(studycase, function_id, csv_in, path_data):
    header = ["Parameters"]
    param = ["Implementation (currency/ha)", "Maintenance (currency/ha)",
             "Opportunity (currency/ha)", "Maintenance Time (yr)"]
    cost_nbs = ["unit_implementation_cost",
                "unit_maintenance_cost", "unit_oportunity_cost"]
    results = getDataDB([studycase], function_id)

    results1tot = []
    time = []
    times = []
    headers = []
    for cab in cost_nbs:
        opt = []
        for res in results:
            res = list(res)
            if(cab == res[2]):
                opt.append(res[3])
                headers.append(res[0])
        results1tot.append(opt)

    headers = list(set(headers))
    for hed in headers:
        for tim in results:
            if (hed == tim[0]):
                time.append(tim[1])
        times += list(set(time))
    results1tot.append(times)

    headers = sorted(headers)
    header += headers
    for idx, rest in enumerate(results1tot):
        rest.insert(0, param[idx])

    pathcsv = path.join(path_data, ROI, IN, csv_in)
    generateCsv(header, results1tot, pathcsv)

# 6 Genera el archivo csv de Porfolio_NBS

def genCSVPort_NBS(studycase, function_id1, function_id2, csv_in, path_data):
    header = ["Time"]
    results1 = getDataDB([studycase], function_id1)
    results2 = getDataDB([studycase], function_id2)

    # Se ordenan los resultados obtenidos en la DB
    # para poder generar la estructura solicitada en el csv
    results1tot = []
    for first in results1:
        order = list(first)
        for val in results2:
            if (first[3] == val[0]):
                order.append(val[2])

        order.pop(1)
        order.pop(1)
        order.pop(1)
        results1tot.append(order)

    tot = len(results2)/len(results1)

    # Se adicionan las otras cabeceras al archivo
    # n
    for i in range(int(tot)):
        header.append(str(i+1))

    results1tot.insert(0, header)

    df = pd.DataFrame(results1tot, columns=header)
    df_T = df.T
    pathcsv = path.join(path_data, ROI, IN, csv_in)
    df_T.to_csv(pathcsv, header=None, index=False)

# 7 Genera el archivo csv de Financial_Parmeters

def genCSVFin_Par(studycase, function_id1, function_id2, csv_in, path_data):
    header = ["ID", "Cost", "Value"]
    cost = [["Transaction Cost (%)"],
            ["Discount rate (%)"],
            ["Sensitivity Analysis - Minimum Discount Rate (%)"],
            ["Sensitivity Analysis - Maximum Discount Rate (%)"]]
    result1 = getDataDB([studycase], function_id1)
    result2 = getDataDB([studycase], function_id2)

    result2 = list(result2[0])
    results1tot = []
    for idx, res_cost in enumerate(cost):
        res_cost.insert(1, result2[idx])
        results1tot.append(res_cost)

    result1_s = []
    for res in result1:
        result1_s.append(list(res))

    results1tot += result1_s

    for idx, res_cost in enumerate(results1tot):
        res_cost.insert(0, idx+1)

    pathcsv = path.join(path_data, ROI, IN, csv_in)
    generateCsv(header, results1tot, pathcsv)

# 8 Genera el archivo csv de Time

def genCSVTime(studycase, function_id, csv_in, path_data):
    header = ["Time_ROI", "Time_Implementation_NBS"]
    results = getDataDB([studycase], function_id)
    pathcsv = path.join(path_data, ROI, IN, csv_in)
    generateCsv(header, results, pathcsv)

# 9 - 10 Genera el archivo csv de CO2 BAU y NBS

def genCSVCO2(studycase, csv_in, csv_out, date, user_id, path_data):
    # path_principal path.join(ruta, 'salidas', f'{user_id}_{studycase}_{date}')
    dirs = os.listdir(path_data)
    flag=0
    df_carbon = []
    for dir in dirs:
        if 'WI' in dir:
            flag=1
            path_intake = path.join(path_data, dir, OUT, '07-DISAGGREGATION', csv_in)
            df = pd.read_csv(path_intake)
            df = df['WC (Ton)']
            df.name = f'{dir}_WC_(Ton)'
            df_carbon.append(df)
    if flag==1:
        time_array = np.array(list(range(df.size)))
        df_time = pd.DataFrame(time_array, columns=['Time'])
        df_carbon.insert(0, df_time)
        df_carbon = pd.concat(df_carbon, axis=1)
    
    pathcsv_out = path.join(path_data, ROI, IN, csv_out)
    df_carbon.to_csv(pathcsv_out, index=False)
