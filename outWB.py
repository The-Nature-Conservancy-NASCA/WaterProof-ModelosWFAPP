import csv,os,sys
sys.path.append('config')
from config import config
from connect import connect
from ROIFunctions.common_functions import generateCsv

dirOutputs = {
    'results': 'Results_Order.csv',
    'cn': {
        'file': 'CN_Results.csv',
        'field': 'cn_mg_l'
    },
    'csed': {
        'file': 'CSed_Results.csv',
        'field': 'csed_mg_l'
        },
    'cp': {
        'file': 'CP_Results.csv',
        'field': 'cp_mg_l'
        },
    'q' : {
        'file':'Q_Results.csv',
        'field': 'q_l_s'
        },    
    'wn': {
        'file':'WN_Results.csv',
        'field': 'wn_kg'
        },
    'wn_ret': {
        'file':'WN_Ret_Results.csv',
        'field': 'wn_ret_kg'},
    'wp': {
        'file':'WP_Results.csv',
        'field': 'wp_kg'
        },
    'wp_ret': {
        'file':'WP_Ret_Results.csv',
        'field': 'wp_ret_ton'},
    'wsed' : {
        'file':'WSed_Results.csv',
        'field': 'wsed_ton'},
    'wsed_ret': {
        'file':'WSed_Ret_Results.csv',
        'field': 'wsed_ret_ton'
        } 
}

dirOutputsPTAP = {
    'results': 'Results_Order.csv',
    'cn': {
        'file': 'CN_Results.csv',
        'field': 'element_cn_mg_l'
        },
    'csed': {
        'file': 'CSed_Results.csv',
        'field': 'element_csed_mg_l'
        },
    'cp': {
        'file': 'CP_Results.csv',
        'field': 'element_cp_mg_l'
        },
    'q' : {
        'file':'Q_Results.csv',
        'field': 'element_q_l'
        },    
    'wn': {
        'file':'WN_Results.csv',
        'field': 'element_wn_kg'
        },
    'wn_ret': {
        'file':'WN_Ret_Results.csv',
        'field': 'element_wn_rent_kg'},
    'wp': {
        'file':'WP_Results.csv',
        'field': 'element_wp_kg'
        },
    'wp_ret': {
        'file':'WP_Ret_Results.csv',
        'field': 'element_wp_rent_ton'},
    'wsed' : {
        'file':'WSed_Results.csv',
        'field': 'element_wsed_tom'},
    'wsed_ret': {
        'file':'WSed_Ret_Results.csv',
        'field': 'element_wsed_ret_ton'
        }
}

ruta = os.environ["PATH_FILES"]

def readCsv(csvIn, path_data_wb_out):
    pathFile = os.path.join(path_data_wb_out,csvIn)
    resultList = []
    with open(pathFile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            resultList.append(row)

    return resultList


def mergeData(path_data_wb_out):
    order = []
    for key in dirOutputs:
        if key != 'results':
            csv_result = readCsv(dirOutputs[key]['file'],path_data_wb_out)
            if len(csv_result) > 0:
                nums = csv_result[0]
                row = []
                row.append(key)
                row.append('0')
                for num in nums:
                    row.append(num)

                order.append(row)
        else:
            csv_result = readCsv(dirOutputs['results'], path_data_wb_out)[0]
            row = []
            row.append('type')
            row.append('year')
            for o in csv_result:
                row.append(o)

            order.append(row)


    sumFilePath = os.path.join(path_data_wb_out,'sumWB.csv')

    generateCsv(order[0],order[1:],sumFilePath)

    return sumFilePath

def updateParameter(element, parameter, value):
	listResult = []
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	cursor.callproc('__wpupdate_parameter',[element,parameter,value])
	conn.commit()
	cursor.close()
	conn.close()

def readSum(csvIn, path_data_wb_out):
    print ('Reading sum file')
    print("csvIn: ",csvIn)
    print("path_data_wb_out: ",path_data_wb_out)
    data = readCsv(csvIn, path_data_wb_out)
    line = 0
    headers = []
    for row in data:
        line = line + 1
        if line == 1:
            headers = row
        else:
            typeI = row[0]
            year = row[1]
            for i in range (2,len(row)):
                value = row[i]
                element = int(float(headers[i]))
                parameter = dirOutputs[typeI]['field']
                updateParameter(element,parameter,value)

## Funciones para la PTAP

def mergeDataPTAP():
    order = []
    for key in dirOutputsPTAP:
        if key != 'results':
            csv_result = readCsv(dirOutputsPTAP[key]['file'])
            if len(csv_result) > 0:
                nums = csv_result[0]
                row = []
                row.append(key)
                row.append('0')
                for num in nums:
                    row.append(num)

                order.append(row)
        else:
            csv_result = readCsv(dirOutputsPTAP['results'])[0]
            row = []
            row.append('type')
            row.append('year')
            for o in csv_result:
                row.append(o)

            order.append(row)


    sumFilePath = os.path.join(ruta,'salidas','wb_test','OUTPUTS','sumWB.csv')

    generateCsv(order[0],order[1:],sumFilePath)

    return sumFilePath

def updateParameterPTAP(element, parameter, value):
	listResult = []
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	cursor.callproc('__wpupdate_parameter_ptap',[element,parameter,value])
	conn.commit()
	cursor.close()
	conn.close()

def readSumPTAP(csvIn):
    data = readCsv(csvIn)
    line = 0
    headers = []
    for row in data:
        line = line + 1
        if line == 1:
            headers = row
        else:
            typeI = row[0]
            year = row[1]
            for i in range (2,len(row)):
                value = row[i]
                element = int(float(headers[i]))
                parameter = dirOutputsPTAP[typeI]['field']
                updateParameterPTAP(element,parameter,value)


# outFile = mergeData()
# readSum(outFile)
# print("Exitoso")