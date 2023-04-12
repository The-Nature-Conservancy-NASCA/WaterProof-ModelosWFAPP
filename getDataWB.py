import sys, csv
import numpy as np
from os import environ,path
sys.path.append('config')
from config import config
from connect import connect
from ROIFunctions.common_functions import getDataDB,generateCsv,updateDataDB
ruta = environ["PATH_FILES"]



def updateDataDB( id, funcion_db ):
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc(funcion_db,[id])
    conn.commit()
    cursor.close()
    conn.close()
    return True

def generateCsvTopology(id, function_db, path_data_wb_in):
    results = getDataDB([id],function_db)
    csv_in = "0_WI_Topology.csv"
    pathF = path.join(path_data_wb_in, csv_in)
    generateCsv(["From_Element","To_Element"],results, pathF)

def generateCsvPerc(id, function_db, csv_in, path_data_wb_in):
    results = getDataDB( [id], function_db )
    pathF = path.join(path_data_wb_in, csv_in)
    generateCsv(["From_Element","PWater","RetSed","RetN","RetP"],results, pathF)

def generateCsvData(id, funcion_db, csv_in, path_data_in):
    results = getDataDB( [id], funcion_db )
    listElements = []
    listData = []
    listElements.append(0)
    listData.append(0)
    pathF = path.join(path_data_in,csv_in)
    for r in results:
        listElements.append(r[0])
        listData.append(r[1])
    listDataH = []
    listDataH.append(listData)
    generateCsv(listElements,listDataH, pathF)

def generateCsvDataDis(ptap_id, function_db,csv_in, pos, csv_dis, path_data_wb_in, path_data_ds_out):
    listHeader = []
    listResults = []
    listResultsDB = []
    result = getDataDB([ptap_id], function_db)
    result.sort()
    idriver = result.pop(0)
    # se adiciona el elemento 0 al inicio
    listHeader.append(0)
    listHeader.append(idriver[0])
    # Se crea un arreglo con el valor del rio
    for row in result:
        listHeader.append(row[0])
        listResultsDB.append(0)
    # se crea la ruta del archivo a generar
    pathF = path.join(path_data_wb_in, csv_in)
    # se lee el archivo generado por el modelo de disaggregation
    reader = np.loadtxt(open(path.join(path_data_ds_out,csv_dis)), delimiter=",", skiprows=1)
    for r in reader:
        app = [r[0]] + [r[pos]] + listResultsDB
        listResults.append(app)
    generateCsv(listHeader,listResults, pathF)

def generateCsvDataDisPTAP(ptap_id,studycase_id, function_db,csv_in, type, scenario, path_data_wb_in):
    listHeader = []
    listResults = []
    listResultsDB = []
    result = getDataDB([ptap_id], function_db)
    reader = getDataDB([ptap_id, type, scenario, studycase_id], '__wp_ptap_get_data_intakes')
    result.sort()
    idriver = result.pop(0)
    # se adiciona el elemento 0 al inicio
    listHeader.append(0)
    listHeader.append(idriver[0])
    # Se crea un arreglo con el valor del rio
    for row in result:
        listHeader.append(row[0])
        listResultsDB.append(0)
    # se crea la ruta del archivo a generar
    pathF = path.join(path_data_wb_in,csv_in)
    for r in reader:
        app = [r[0]] + [r[1]] + listResultsDB
        listResults.append(app)
    generateCsv(listHeader,listResults, pathF)

def generateCsvQ(args_id, funcion_db, csv_in, path_data_wb_in):
    results = getDataDB(args_id, funcion_db)
    listElements = []
    listData = []
    element = None
    pathF = path.join(path_data_wb_in,csv_in)
    for r in results:
        listData.append([r[1]-1,r[2]])
        # Se adiciona el 1 porque la extración de agua
        # se realiza desde el segundo elemento del flujo
        element = r[0]
    generateCsv(["0",element],listData, pathF)

def generateCsvQDisPTAP(csv_in, path_data_wb_in):
    pathF = path.join(path_data_wb_in,csv_in)
    generateCsv(["0","-1"],[["0","0"]], pathF)
