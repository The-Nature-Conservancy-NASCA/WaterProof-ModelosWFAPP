import csv,datetime
import shutil
from os import path,environ
from connect import connect
base_path = environ["PATH_FILES"]


def insertParameter( function_db, args ):
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc( function_db , args )
    conn.commit()
    cursor.close()
    conn.close()

def getDataDB( args, funcion_db ):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc(funcion_db,args)
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def selectDataDB( query ):
    result = ''
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result[0]

def generateCsv(header, values, file):
    row_list = []
    row_list.append(header)

    for item in values:
        row_list.append(item)
	
    with open(file,"w",newline='') as file:
        writer = csv.writer(file)
        writer.writerows(row_list)

def updateDataDB( args, funcion_db ):
    print( "updateDataDB :: start" )
    print ("args : ")
    print (args)
    print ("funcion_db : %s" % funcion_db)
    
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc(funcion_db,args)
    conn.commit()
    cursor.close()
    conn.close()
    return True

def path_wb(id_intake,user_id,study_case_id, preffix):
	DISAGGREGATION_DIR = "07-DISAGGREGATION"
	WATER_BALANCE_DIR = "08-WATER_BALANCE"
	OUT_BASE_DIR = "salidas"
	wi_folder = "%s_%s" % (preffix, id_intake)
	date = datetime.date.today()
	usr_folder = "%s_%s_%s-%s-%s" % (user_id,study_case_id, date.year, date.month, date.day)
	path_data_wb_in = path.join(base_path, OUT_BASE_DIR, usr_folder, wi_folder, "in", WATER_BALANCE_DIR)
	path_data_wb_out = path.join(base_path, OUT_BASE_DIR, usr_folder, wi_folder, "out", WATER_BALANCE_DIR)
	path_data_ds_out = path.join(base_path, OUT_BASE_DIR, usr_folder, wi_folder, "out", DISAGGREGATION_DIR)
	return path_data_wb_in, path_data_wb_out, path_data_ds_out

def CopyFile(original,target):
    shutil.copyfile(original,target)