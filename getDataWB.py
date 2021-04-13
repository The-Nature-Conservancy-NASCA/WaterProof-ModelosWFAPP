import sys, csv
import numpy as np
from os import environ,path
sys.path.append('config')
from config import config
from connect import connect

ruta = environ["PATH_FILES"]


def getDataDB( id, funcion_db ):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc(funcion_db,[id])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    if (listResult ==[]):
        raise Exception(f'Sin datos para el id: {id}')

    return listResult

def generateCsv( header, values, file ):
    row_list = []
    row_list.append(header)

    for item in values:
        row_list.append(item)
	
    with open(file,"w",newline='') as file:
        writer = csv.writer(file)
        writer.writerows(row_list)

def generateCsvTopology( id, function_db, csv_in ):
    results = getDataDB(id,function_db)
    print(results)
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","0_WI_Topology.csv")
    generateCsv(["From_Element","To_Element"],results, pathF)

def generateCsvPerc( id, function_db, csv_in ):
    results = getDataDB( id, function_db )
    # print(results)
    pathF = path.join(ruta,"salidas","wb_test","INPUTS",csv_in)
    generateCsv(["From_Element","PWater","RetSed","RetN","RetP"],results, pathF)

def generateCsvData( id, funcion_db, csv_in ):
    results = getDataDB( id, funcion_db )
    listElements = []
    listData = []
    listElements.append(0)
    listData.append(0)
    pathF = path.join(ruta,"salidas","wb_test","INPUTS",csv_in)
    for r in results:
        listElements.append(r[0])
        listData.append(r[1])
    listDataH = []
    listDataH.append(listData)
    generateCsv(listElements,listDataH, pathF)

def generateCsvDataDis( ptap_id, function_db,csv_in, pos, csv_dis ):
    listHeader = []
    listResults = []
    listResultsDB = []
    result = getDataDB(ptap_id,function_db)
    result.sort()
    idriver = result.pop(0)
    # se adiciona el elemento 0 al inicio
    listHeader.append(0)
    listHeader.append(idriver[0])
    # Se crea un arreglo con el valor del rio
    for row in result:
        listHeader.append(row[0])
        listResultsDB.append(row[1])
    # se crea la ruta del archivo a generar
    pathF = path.join(ruta,"salidas","wb_test","INPUTS",csv_in)
    # se lee el archivo generado por el modelo de disaggregation
    reader = np.loadtxt(open(path.join(ruta,"salidas","disaggregation","Out","disaggregation",csv_dis)), delimiter=",", skiprows=1)
    for r in reader:
        app = [r[0]] + [r[pos]] + listResultsDB
        listResults.append(app)
    generateCsv(listHeader,listResults, pathF)

def generateCsvQ( id, funcion_db, csv_in):
    results = getDataDB( id, funcion_db )
    listElements = []
    listData = []
    element = None
    pathF = path.join(ruta,"salidas","wb_test","INPUTS",csv_in)
    for r in results:

        listData.append([r[1]-1,r[2]])
        # Se adiciona el 1 porque la extración de agua
        # se realiza desde el segundo elemento del flujo
        element = r[0]
    generateCsv(["0",element],listData, pathF)

def generateCsvQDisPTAP(csv_in):
    pathF = path.join(ruta,"salidas","wb_test","INPUTS",csv_in)
    generateCsv(["0",'-1'],['0','0'], pathF)


