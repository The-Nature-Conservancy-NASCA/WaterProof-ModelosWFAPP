import sys,csv,os
sys.path.append('config')
from config import config
from connect import connect
from ROIFunctions.common_functions import getDataDB,generateCsv

ruta = os.environ["PATH_FILES"]

# def list2str(list_csinfras):
#     resultado = ""
#     for cs in list_csinfras:
#         resultado = resultado + str(cs) + ","

#     resultado = resultado[:-1]

#     return resultado

def getDataCsInfra(csinfra_id):
    print("getDataCsInfra")
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('__wp_getcsinfra',[csinfra_id])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def allData(list_csinfras):
    print("allData")
    result = []
    for cs in list_csinfras:
        data = getDataCsInfra(cs)
        result.append(data)

    return result

# def generateAWYCsv(list_cs):
#     results = getTopologyData(catchment_id)
#     # print(results)
#     pathF = os.path.join(ruta,"salidas","wb_test","INPUTS","0_WI_Topology.csv")
#     generateCsv(["From_Element","To_Element"],results, pathF)

def generateAll(list_cs):
    print("generateAll")
    data = allData(list_cs)
    headers = []
    h = []
    h.append("Time")
    awy = []
    awy_item = []
    awy_item.append("1")
    sed = []
    sed_item = []
    sed_item.append("1")
    n = []
    n_item = []
    n_item.append("1")
    p = []
    p_item = []
    p_item.append("1")
    norm = getDataDB([list_cs[0]],"__wp_ptap_normquality")
    for d in data:
        h.append("Csinfra-" + str(d[0][0]))
        awy_item.append(d[0][7])
        sed_item.append(d[0][16])
        n_item.append(d[0][12])
        p_item.append(d[0][17])

    headers.append(h)
    awy.append(awy_item)
    sed.append(sed_item)
    n.append(n_item)
    p.append(p_item)

    generateCsv(headers[0],awy,os.path.join(ruta,"salidas","ptap_test","INPUTS","1_WI_AWY.csv"))
    generateCsv(headers[0],sed,os.path.join(ruta,"salidas","ptap_test","INPUTS","2_WI_WSed.csv"))
    generateCsv(headers[0],n,os.path.join(ruta,"salidas","ptap_test","INPUTS","3_WI_WN.csv"))
    generateCsv(headers[0],p,os.path.join(ruta,"salidas","ptap_test","INPUTS","4_WI_WP.csv"))
    generateCsv(['Quatily'],norm,os.path.join(ruta,"salidas","ptap_test","INPUTS","7_NormQuality.csv"))

    return p




