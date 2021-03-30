
import csv,os,sys
sys.path.append('config')
from config import config
from connect import connect
import pandas as pd

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

ruta = os.environ["PATH_FILES"]

def readCsv(csvIn):
    pathFile = os.path.join(ruta,'salidas','wb_test','OUTPUTS',csvIn)
    resultList = []
    with open(pathFile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            resultList.append(row)

    return resultList

def generateCsv(header,values, file):
    row_list = []
    row_list.append(header)

    for item in values:
        row_list.append(item)

    with open(file,"w",newline='') as file:
        writer = csv.writer(file)
        writer.writerows(row_list)

def mergeDataDis():
    cn = readCsv('CN_Results.csv')
    csed = readCsv('CSed_Results.csv')
    cp = readCsv('CP_Results.csv')
    q = readCsv('Q_Results.csv')
    wn = readCsv('WN_Results.csv')
    wn_ret = readCsv('WN_Ret_Results.csv')
    wp = readCsv('WP_Results.csv')
    wp_ret = readCsv('WP_Ret_Results.csv')
    wsed = readCsv('WSed_Results.csv')
    wsed_ret = readCsv('WSed_Ret_Results.csv')

    for a in cn,csed,cp,q,wn,wn_ret,wp,wp_ret,wsed,wsed_ret:
        print(a)
        for b in a:
            print(b)



    return a
    

    # order = []
    # orderbyyear = []
    # for key in dirOutputs:
    #     if key != 'results':
    #         csv_result = readCsv(dirOutputs[key]['file'])
    #         if len(csv_result) > 0:
    #             row = []
    #             data = []
    #             count = 0
    #             for num in csv_result:
    #                 for i in num:
    #                     data.append(i)
    #                 rowc = [key]+[count]+data
    #                 order.append(rowc)
    #                 data = []
    #                 count += 1
    #     else:
    #         csv_result = readCsv(dirOutputs['results'])[0]
    #         row = []
    #         row.append('type')
    #         row.append('year')
    #         for o in csv_result:
    #             row.append(o)

    #         order.append(row)


    # sumFilePath = os.path.join(ruta,'salidas','wb_test','OUTPUTS','sumWB.csv')

    # generateCsv(order[0],order[1:],sumFilePath)

    # return sumFilePath

def insertParameter(element, parameter, value):
	listResult = []
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	cursor.callproc('__wp_intake_insert_report',[element,parameter,value])
	conn.commit()
	cursor.close()
	conn.close()

def readSumDis(csvIn):
    data = readCsv(csvIn)
    line = 0
    headers = []
    for row in data:
        line += + 1
        if line == 1:
            headers = row
        else:
            typeI = row[0]
            year = row[1]
            for i in range (2,len(row)):
                value = row[i]
                element = int(float(headers[i]))
                parameter = dirOutputs[typeI]['field']
                insertParameter(element,parameter,value)