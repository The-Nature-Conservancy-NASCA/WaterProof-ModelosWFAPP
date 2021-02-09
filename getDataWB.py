import sys, csv
from os import environ,path
sys.path.append('config')
from config import config
from connect import connect

ruta = environ["PATH_FILES"]

def getTopologyData(catchment_id):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('gettopologybycatchment',[catchment_id])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def getTopologyData(catchment_id):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('gettopologybycatchment',[catchment_id])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult


def getPercData(catchment_id):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('getpercentagesbycatchment',[catchment_id])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def getAWYData(catchment_id):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('getawybycatchment',[catchment_id])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def getSedData(catchment_id):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('getsedbycatchment',[catchment_id])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def getNData(catchment_id):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('getnbycatchment',[catchment_id])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def getPData(catchment_id):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('getpbycatchment',[catchment_id])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def getQData(catchment_id):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('getqbycatchment',[catchment_id])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def generateCsv(header,values, file):
    row_list = []
    row_list.append(header)

    for item in values:
        row_list.append(item)
	
    with open(file,"w",newline='') as file:
        writer = csv.writer(file)
        writer.writerows(row_list)

def generateCsvTopology(catchment_id):
    results = getTopologyData(catchment_id)
    # print(results)
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","0_WI_Topology.csv")
    generateCsv(["From_Element","To_Element"],results, pathF)

def generateCsvPerc(catchment_id):
    results = getPercData(catchment_id)
    # print(results)
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","1_WI_Elements_Param.csv")
    generateCsv(["From_Element","PWater","RetSed","RetN","RetP"],results, pathF)

def generateCsvAWY(catchment_id):
    results = getAWYData(catchment_id)
    listElements = []
    listData = []
    listElements.append(0)
    listData.append(0)
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","2_WI_AWYInputs.csv")
    for r in results:
        listElements.append(r[0])
        listData.append(r[1])
    listDataH = []
    listDataH.append(listData)
    generateCsv(listElements,listDataH, pathF)

def generateCsvSed(catchment_id):
    results = getSedData(catchment_id)
    listElements = []
    listData = []
    listElements.append(0)
    listData.append(0)
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","2_WI_WSedInputs.csv")
    for r in results:
        listElements.append(r[0])
        listData.append(r[1])
    listDataH = []
    listDataH.append(listData)
    generateCsv(listElements,listDataH, pathF)

def generateCsvN(catchment_id):
    results = getNData(catchment_id)
    listElements = []
    listData = []
    listElements.append(0)
    listData.append(0)
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","2_WI_WNInputs.csv")
    for r in results:
        listElements.append(r[0])
        listData.append(r[1])
    listDataH = []
    listDataH.append(listData)
    generateCsv(listElements,listDataH, pathF)

def generateCsvP(catchment_id):
    results = getPData(catchment_id)
    listElements = []
    listData = []
    listElements.append(0)
    listData.append(0)
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","2_WI_WPInputs.csv")
    for r in results:
        listElements.append(r[0])
        listData.append(r[1])
    listDataH = []
    listDataH.append(listData)
    generateCsv(listElements,listDataH, pathF)

def generateCsvQ(catchment_id):
    results = getQData(catchment_id)
    listElements = []
    listData = []
    element = None
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","3_Water_Extraction.csv")
    for r in results:
        listData.append([r[1],r[2]])
        element = r[0]
    generateCsv(["0",element],listData, pathF)

def generateAllData(catchment_id):
    generateCsvTopology(catchment_id)
    generateCsvPerc(catchment_id)
    generateCsvAWY(catchment_id)
    generateCsvSed(catchment_id)
    generateCsvN(catchment_id)
    generateCsvP(catchment_id)
    generateCsvQ(catchment_id)

#catchment_id = 3

#generateAllData(catchment_id)


