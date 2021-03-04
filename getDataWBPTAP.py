import sys, csv
from os import environ,path
sys.path.append('config')
from config import config
from connect import connect

ruta = environ["PATH_FILES"]

def getTopologyData(id_ptap):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('__wpgettopologybyptap',[id_ptap])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def getPercData(id_ptap):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('__wpgetpercentagesbyptap',[id_ptap])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def getAWYData(id_ptap):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('__wpgetawybyptap',[id_ptap])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def getSedData(id_ptap):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('__wpgetsedbycatchment',[id_ptap])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def getNData(id_ptap):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('__wpgetnbyptap',[id_ptap])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def getPData(id_ptap):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('__wpgetpbyptap',[id_ptap])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def getQData(id_ptap):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('__wpgetqbyptap',[id_ptap])
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

def generateCsvTopology(id_ptap):
    results = getTopologyData(id_ptap)
    print(results)
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","0_WI_Topology.csv")
    generateCsv(["From_Element","To_Element"],results, pathF)

def generateCsvPerc(id_ptap):
    results = getPercData(id_ptap)
    # print(results)
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","1_WI_Elements_Param.csv")
    generateCsv(["From_Element","PWater","RetSed","RetN","RetP"],results, pathF)

def generateCsvAWY(id_ptap):
    results = getAWYData(id_ptap)
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

def generateCsvSed(id_ptap):
    results = getSedData(id_ptap)
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

def generateCsvN(id_ptap):
    results = getNData(id_ptap)
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

def generateCsvP(id_ptap):
    results = getPData(id_ptap)
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

def generateCsvQ(id_ptap):
    results = getQData(id_ptap)
    listElements = []
    listData = []
    element = None
    pathF = path.join(ruta,"salidas","wb_test","INPUTS","3_Water_Extraction.csv")
    for r in results:
        listData.append([r[1],r[2]])
        element = r[0]
    generateCsv(["0",element],listData, pathF)

def generateAllData(id_ptap):
    generateCsvTopology(id_ptap)
    generateCsvPerc(id_ptap)
    generateCsvAWY(id_ptap)
    generateCsvSed(id_ptap)
    generateCsvN(id_ptap)
    generateCsvP(id_ptap)
    generateCsvQ(id_ptap)

#id_ptap = 3

#generateAllData(id_ptap)