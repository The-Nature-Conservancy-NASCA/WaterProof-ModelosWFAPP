import csv,os,sys
sys.path.append('config')
from config import config
from connect import connect
import pandas as pd
import numpy as np
from pandas.core.common import flatten

ruta = os.environ["PATH_FILES"]
# ruta = 'D:/Descargas/Trabajo/Workspace/tnc/modelos'

def SaveInDB( function_db, ptap_id, user_id, study_case_id, scenario ):
    # Ruta de acceso a los archivos
    anotherroute= os.path.join(ruta,'salidas','wb_test','OUTPUTS')
    # archivos de salida en csv a Matriz
    headers = pd.read_csv(anotherroute+'/Results_Order.csv',nrows=0).columns
    cn = pd.read_csv(anotherroute+'/CN_Results.csv', names=headers)
    csed = pd.read_csv(anotherroute+'/CSed_Results.csv', names=headers)
    cp = pd.read_csv(anotherroute+'/CP_Results.csv', names=headers)
    q = pd.read_csv(anotherroute+'/Q_Results.csv', names=headers)
    wn = pd.read_csv(anotherroute+'/WN_Results.csv', names=headers)
    wn_ret = pd.read_csv(anotherroute+'/WN_Ret_Results.csv', names=headers)
    wp = pd.read_csv(anotherroute+'/WP_Results.csv', names=headers)
    wp_ret = pd.read_csv(anotherroute+'/WP_Ret_Results.csv', names=headers)
    wsed = pd.read_csv(anotherroute+'/WSed_Results.csv', names=headers)
    wsed_ret = pd.read_csv(anotherroute+'/WSed_Ret_Results.csv', names=headers)

    # las cabeceras se pasan a tipo Lista para poder unirlas
    headerList=headers.tolist()
    headersdat=[]
    yeardat=[]
    # print(len(cn))
    count = 0
    year=[]
    for b in range(len(cn)):
        count+=1
        year.append(count)

    for a in range(len(headerList)):
        yeardat.append(year)

    # se repiten las cabeceras el numero de veces (años)
    for a in range(len(cn)):
        headersdat.append(headerList)

    # Se aplanan todas las matrices para trabajarlas como arreglos
    headerdat = np.array(headersdat).flatten()
    yeardat = np.array(yeardat).flatten()
    cndat = cn.to_numpy().flatten()
    cseddat = csed.to_numpy().flatten()
    cpdat = cp.to_numpy().flatten()
    qdat = q.to_numpy().flatten()
    wndat = wn.to_numpy().flatten()
    wn_retdat = wn_ret.to_numpy().flatten()
    wpdat = wp.to_numpy().flatten()
    wp_retdat = wp_ret.to_numpy().flatten()
    wseddat = wsed.to_numpy().flatten()
    wsed_retdat = wsed_ret.to_numpy().flatten()
    yeardat.sort()
    # se crea la matriz con todos los arreglos
    final = pd.DataFrame(data=np.array([headerdat,yeardat,qdat,cndat,cpdat,cseddat,wndat,wpdat,wseddat,wn_retdat,wp_retdat,wsed_retdat]))
    for label,series in final.items():
        val = series.values
        # Por el momento se han agregado ceros en los datos que aun no han sido obtenidos
        insertParameter( function_db, float(val[0]), ptap_id, val[1], user_id, val[2], val[3], val[4], val[5], val[6], val[7], val[8], val[9], val[10], val[11], study_case_id, scenario )

def insertParameter( function_db, element_id, ptap_id, year, user_id, awy, cn_mg_l, cp_mg_l, csed_mg_l, wn_kg, wp_kg, wsed_ton, wn_ret_kg, wp_ret_kg, wsed_ret_ton, study_case_id, scenario ):
	listResult = []
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	cursor.callproc( function_db ,[ element_id, ptap_id, year, user_id, awy, cn_mg_l, cp_mg_l, csed_mg_l, wn_kg, wp_kg, wsed_ton, wn_ret_kg, wp_ret_kg, wsed_ret_ton, study_case_id, scenario ])
	conn.commit()
	cursor.close()
	conn.close()

# if __name__ == "__main__":
#     mergeDataDis()