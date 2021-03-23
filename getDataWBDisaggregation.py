import sys, csv
import numpy as np
from os import environ,path
sys.path.append('config')
from config import config
from connect import connect
from getDataWB import generateCsv, getTopologyData, getPercData, getQData

# Genera los csv para la primera ejecucion desde DissagBAU

def generateCsvAWYBau(catchment_id):
    result = ''
    listHeader = []
    listResult = []
    listResultexamples = []
    # conexion a la base de datos para llamar la funcion
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('__wpgetawybycatchmentdis',[catchment_id])
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    # se adiciona el elemento 0 al inicio
    listHeader.append(0)
    # Se crea un arreglo con el valor del rio
    for row in result:
        listHeader.append(row[0]-1)
    # se crea el arreglo con el valor del resto de los elementos
    for row in result:
        listHeader.append(row[0])
        listResultexamples.append(row[1])
    # se eliminan los elementos duplicados para la uniformidad de los datos
    listHeaderFin = list(set(listHeader))
    # se crea la ruta del archivo a generar
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","2_WI_AWYInputs.csv")
    # se lee el archivo generado por el modelo de disaggregation
    reader = np.loadtxt(open(path.join(ruta,"salidas","disaggregation",'02-OUTPUTS_BaU.csv')), delimiter=",", skiprows=1)
    for r in reader:
        app = [r[0]] + [r[1]] + listResultexamples
        listResult.append(app)
    generateCsv(listHeaderFin,listResult, pathF)
    
    #WSed

    def generateCsvWSedBau(catchment_id):
    result = ''
    listHeader = []
    listResult = []
    listResultexamples = []
    # conexion a la base de datos para llamar la funcion
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('__wp_catchment_disaggregation_awy',[catchment_id])
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    # se adiciona el elemento 0 al inicio
    listHeader.append(0)
    # Se crea un arreglo con el valor del rio
    for row in result:
        listHeader.append(row[0]-1)
    # se crea el arreglo con el valor del resto de los elementos
    for row in result:
        listHeader.append(row[0])
        listResultexamples.append(row[1])
    # se eliminan los elementos duplicados para la uniformidad de los datos
    listHeaderFin = list(set(listHeader))
    # se crea la ruta del archivo a generar
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","2_WI_WSedInputs.csv")
    # se lee el archivo generado por el modelo de disaggregation
    reader = np.loadtxt(open(path.join(ruta,"salidas","disaggregation",'02-OUTPUTS_BaU.csv')), delimiter=",", skiprows=1)
    for r in reader:
        app = [r[0]] + [r[2]] + listResultexamples
        listResult.append(app)
    generateCsv(listHeaderFin,listResult, pathF)

    #WN
    #WP


# Genera los csv para la primera ejecucion desde DissagNBS
def generateCsvAWYNBS(catchment_id):
    result = ''
    listHeader = []
    listResultFin = []
    listResultexamples = []
    # conexion a la base de datos para llamar la funcion
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('__wpgetawybycatchmentdis',[catchment_id])
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    # se adiciona el elemento 0 al inicio
    listHeader.append(0)
    # Se crea un arreglo con el valor del rio
    for row in result:
        listHeader.append(row[0]-1)
    # se crea el arreglo con el valor del resto de los elementos
    for row in result:
        listHeader.append(row[0])
        listResultexamples.append(row[1])
    # se eliminan los elementos duplicados para la uniformidad
    listHeaderFin = list(set(listHeader))
    # se crea la ruta del archivo a generar
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","2_WI_AWYInputs.csv")
    # se lee el archivo generado por el modelo de disaggregation
    reader = np.loadtxt(open(path.join(ruta,"salidas","disaggregation",'02-OUTPUTS_NBS.csv')), delimiter=",", skiprows=1)
    for r in reader:
        app = [r[0]] + [r[1]] + listResultexamples
        listResultFin.append(app)
    generateCsv(listHeaderFin,listResultFin, pathF)


# Genera los csv para la primera ejecucion desde DissagNBS
def generateAllDataDisaggBau(catchment_id):
    generateCsvTopology(catchment_id)
    generateCsvPerc(catchment_id)
    generateCsvAWYBau(catchment_id)
    # generateCsvSedBau(catchment_id)
    # generateCsvNBau(catchment_id)
    # generateCsvPBau(catchment_id)
    generateCsvQ(catchment_id)


# Genera los csv para la primera ejecucion desde DissagNBS
def generateAllDataDisaggNBS(catchment_id):
    generateCsvTopology(catchment_id)
    generateCsvPerc(catchment_id)
    generateCsvAWYNBS(catchment_id)
    # generateCsvSedNBS(catchment_id)
    # generateCsvNNBS(catchment_id)
    # generateCsvPNBS(catchment_id)
    generateCsvQ(catchment_id)