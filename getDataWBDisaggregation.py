import sys, csv
import numpy as np
from os import environ,path
sys.path.append('config')
from config import config
from connect import connect
from getDataWB import generateCsv, generateCsvTopology, generateCsvPerc, generateCsvQ,getAWYData, getSedData,getNData,getPData,generateCsvQDis

ruta = environ["PATH_FILES"]
# Genera los csv para la primera ejecucion desde Disaggregation BAU
def generateCsvAWYBau(catchment_id):
    listHeader = []
    listResults = []
    listResultsDB = []
    result = getAWYData(catchment_id)
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
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","2_WI_AWYInputs.csv")
    # se lee el archivo generado por el modelo de disaggregation
    reader = np.loadtxt(open(path.join(ruta,"salidas","disaggregation","Out","disaggregation",'02-OUTPUTS_BaU.csv')), delimiter=",", skiprows=1)
    for r in reader:
        app = [r[0]] + [r[1]] + listResultsDB
        listResults.append(app)
    generateCsv(listHeader,listResults, pathF)

def generateCsvWSedBau(catchment_id):
    listHeader = []
    listResults = []
    listResultsDB = []
    result = getSedData(catchment_id)
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
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","2_WI_WSedInputs.csv")
    # se lee el archivo generado por el modelo de disaggregation
    reader = np.loadtxt(open(path.join(ruta,"salidas","disaggregation","Out","disaggregation",'02-OUTPUTS_BaU.csv')), delimiter=",", skiprows=1)
    for r in reader:
        app = [r[0]] + [r[2]] + listResultsDB
        listResults.append(app)
    generateCsv(listHeader,listResults, pathF)

def generateCsvNBau(catchment_id):
    listHeader = []
    listResults = []
    listResultsDB = []
    result = getNData(catchment_id)
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
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","2_WI_WNInputs.csv")
    # se lee el archivo generado por el modelo de disaggregation
    reader = np.loadtxt(open(path.join(ruta,"salidas","disaggregation","Out","disaggregation",'02-OUTPUTS_BaU.csv')), delimiter=",", skiprows=1)
    for r in reader:
        app = [r[0]] + [r[3]] + listResultsDB
        listResults.append(app)
    generateCsv(listHeader,listResults, pathF)

def generateCsvPBau(catchment_id):
    listHeader = []
    listResults = []
    listResultsDB = []
    result = getPData(catchment_id)
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
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","2_WI_WPInputs.csv")
    # se lee el archivo generado por el modelo de disaggregation
    reader = np.loadtxt(open(path.join(ruta,"salidas","disaggregation","Out","disaggregation",'02-OUTPUTS_BaU.csv')), delimiter=",", skiprows=1)
    for r in reader:
        app = [r[0]] + [r[4]] + listResultsDB
        listResults.append(app)
    generateCsv(listHeader,listResults, pathF)


# Genera los csv para la segunda ejecucion desde Disaggregation NBS
def generateCsvAWYNBS(catchment_id):
    listHeader = []
    listResults = []
    listResultsDB = []
    result = getAWYData(catchment_id)
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
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","2_WI_AWYInputs.csv")
    # se lee el archivo generado por el modelo de disaggregation
    reader = np.loadtxt(open(path.join(ruta,"salidas","disaggregation","Out","disaggregation",'02-OUTPUTS_NBS.csv')), delimiter=",", skiprows=1)
    for r in reader:
        app = [r[0]] + [r[1]] + listResultsDB
        listResults.append(app)
    generateCsv(listHeader,listResults, pathF)

def generateCsvSedNBS(catchment_id):
    listHeader = []
    listResults = []
    listResultsDB = []
    result = getSedData(catchment_id)
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
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","2_WI_WSedInputs.csv")
    # se lee el archivo generado por el modelo de disaggregation
    reader = np.loadtxt(open(path.join(ruta,"salidas","disaggregation","Out","disaggregation",'02-OUTPUTS_NBS.csv')), delimiter=",", skiprows=1)
    for r in reader:
        app = [r[0]] + [r[2]] + listResultsDB
        listResults.append(app)
    generateCsv(listHeader,listResults, pathF)

def generateCsvNNBS(catchment_id):
    listHeader = []
    listResults = []
    listResultsDB = []
    result = getNData(catchment_id)
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
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","2_WI_WNInputs.csv")
    # se lee el archivo generado por el modelo de disaggregation
    reader = np.loadtxt(open(path.join(ruta,"salidas","disaggregation","Out","disaggregation",'02-OUTPUTS_NBS.csv')), delimiter=",", skiprows=1)
    for r in reader:
        app = [r[0]] + [r[3]] + listResultsDB
        listResults.append(app)
    generateCsv(listHeader,listResults, pathF)

def generateCsvPNBS(catchment_id):
    listHeader = []
    listResults = []
    listResultsDB = []
    result = getPData(catchment_id)
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
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","2_WI_WPInputs.csv")
    # se lee el archivo generado por el modelo de disaggregation
    reader = np.loadtxt(open(path.join(ruta,"salidas","disaggregation","Out","disaggregation",'02-OUTPUTS_NBS.csv')), delimiter=",", skiprows=1)
    for r in reader:
        app = [r[0]] + [r[4]] + listResultsDB
        listResults.append(app)
    generateCsv(listHeader,listResults, pathF)

# Genera los csv para la primera ejecucion desde DissagNBS
def generateAllDataDisaggBau(catchment_id):
    generateCsvTopology(catchment_id)
    generateCsvPerc(catchment_id)
    generateCsvAWYBau(catchment_id)
    generateCsvWSedBau(catchment_id)
    generateCsvNBau(catchment_id)
    generateCsvPBau(catchment_id)
    generateCsvQDis(catchment_id)

# Genera los csv para la segunda ejecucion desde DissagNBS
def generateAllDataDisaggNBS(catchment_id):
    generateCsvTopology(catchment_id)
    generateCsvPerc(catchment_id)
    generateCsvAWYNBS(catchment_id)
    generateCsvSedNBS(catchment_id)
    generateCsvNNBS(catchment_id)
    generateCsvPNBS(catchment_id)
    generateCsvQDis(catchment_id)