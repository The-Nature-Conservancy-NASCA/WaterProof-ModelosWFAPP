import csv
from connect import connect

def insertParameter( function_db, args ):
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc( function_db , args )
    conn.commit()
    cursor.close()
    conn.close()

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

def generateCsv(header, values, file):
    row_list = []
    row_list.append(header)

    for item in values:
        row_list.append(item)
	
    with open(file,"w",newline='') as file:
        writer = csv.writer(file)
        writer.writerows(row_list)