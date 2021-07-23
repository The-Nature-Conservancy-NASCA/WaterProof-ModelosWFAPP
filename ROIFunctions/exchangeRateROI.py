import numpy as np
import pandas as pd
from datetime import date
from ROIFunctions.common_functions import insertParameter,getDataDB
 
'''
type_or_id: En este campo van los nombres de los costos o en el caso de la sbn, el id de la sbn
cost: En este campo van los nombres de los costos, llamados del campo correspondiente a cada uno en la base de datos
res_last: En este campo va el resultado de la operación
currency_db: En este campo va el nombre de la moneda del caso de estudio
studycase_id : en este campo va el id del caso de estudio
Date_execution: Fecha de ejecución
'''
def ExchangeROI(studyCase_id):
    carbon = getDataDB([studyCase_id],'__wp_roi_tc_carbon')
    financial = getDataDB([studyCase_id],'__wp_roi_tc_financial_param')
    nbs = getDataDB([studyCase_id],'__wp_roi_tc_cost_nbs')
    rate = getDataDB([studyCase_id],'__wp_roi_tc_exchange_rate')
    fmultglo = getDataDB([studyCase_id],'__wp_roi_tc_global_multi_factor')
    type_or_id =[]
    cost =["Carbon Cost (USD/TonCO2)",
            "Program Director (Cost/yr)",
            "Monitoring and Evaluation Manager (Cost/yr)",
            "Finance and Administrator (Cost/yr)",
            "Implementation Manager (Cost/yr)",
            "Office Costs (Cost/yr)",
            "Travel (Cost/yr)",
            "Equipment (Cost/yr)",
            "Contracts (Cost/yr)",
            "Overhead (Cost/yr)",
            "Others (Cost/yr)"]
    currency_db=[]
    res_first=[]
    res_firstnbs=[]
    # validar cuando no hay conversión de divisas
    if (rate == []):
        rate.append(('NAN','NAN',1))
    # Recorrer el resultado de las tasas de cambio dispobiles para un caso de estudio
    for res_rate in rate:
 
    # multiplicación dato carbón
        for res_carbon in carbon:
            res_carbon=list(res_carbon)
            # validación de mismo currency (no convertir)
            if(res_carbon[0] == res_rate[0] or res_rate[0]=='NAN'):
                res_first.append(res_carbon[1])
                currency_db.append(res_carbon[0])
                type_or_id.append('Carbon')
            else:
                if(res_carbon[0]==res_rate[1]):
                    res_first.append(res_carbon[1]/res_rate[2])
                    currency_db.append(res_rate[0])
                    type_or_id.append('Carbon')
 
    # multiplicación dato financial  
        for res_finan in financial:
            res_finan=list( res_finan )
            # validación de mismo currency (no convertir)
            if(res_finan[0] == res_rate[0] or res_rate[0]=='NAN'):
                curren = res_finan.pop(0)
                for sad in res_finan:
                    res_first.append( sad )
                    currency_db.append(curren)
                    type_or_id.append('Financial')
            else:
                if(res_finan[0]==res_rate[1]):
                    res_finan.pop(0)
                    for sad in res_finan:
                        res_first.append( sad/res_rate[2] )
                        currency_db.append(res_rate[0])
                        type_or_id.append('Financial')
 
    # multiplicación dato nbs
        for res_nbs in nbs:
            cost_nbs =["unit_implementation_cost","unit_maintenance_cost","unit_oportunity_cost"]
            res_nbs=list( res_nbs )
            # validación de mismo currency (no convertir)
            if(res_nbs[4] == res_rate[0] or res_rate[0]=='NAN'):
                # for cost_in_nbs in range(len(res_nbs)-1):
                #     cost + cost_nbs
                curren=res_nbs.pop(4)
                id_nbs=res_nbs.pop(0)
                for index, sad in enumerate(res_nbs):
                    res_firstnbs.append( sad )
                    currency_db.append(curren)
                    type_or_id.append(str(id_nbs))
                    cost.append(cost_nbs[index])
            else:
                if(res_nbs[4]==res_rate[1]):
                    curren=res_nbs.pop(4)
                    id_nbs=res_nbs.pop(0)
                    for idx, sad in enumerate(res_nbs):
                        res_firstnbs.append( sad/res_rate[2] )
                        currency_db.append(res_rate[0])
                        type_or_id.append(str(id_nbs))
                        cost.append(cost_nbs[idx])
 
    # multiplicación con el Factor Multiplicador global
    res_lastnbs=[]
    for fin in res_firstnbs:
        res_lastnbs.append(fin*fmultglo[0][0])
    res_last=res_first+res_lastnbs
    today = date.today()
    date_exec = today.strftime("%Y/%m/%d")
    
    # ordenar la matriz de resultados para insertarlos en la DB
    final = pd.DataFrame(data=np.array([type_or_id,cost,res_last,currency_db]))
    for label,series in final.items():
        val = series.values
        args = [
            val[0], val[1],float(val[2]), val[3], studyCase_id, date_exec
        ]
        # Insertar los resultados en la DB
        insertParameter( '__wp_roi_tc_insert', args )
        