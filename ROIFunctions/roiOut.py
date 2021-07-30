import sys
from os import environ, path
sys.path.append('config')
from config import config
from connect import connect
import shutil,os
import ROIFunctions.cost as cost
import ROIFunctions.saves as save
import ROIFunctions.sensivity as sens
import ROIFunctions.carbon as carb
import constants 
#from ROIFunctions.common_functions import updateDataDB

ruta = environ["PATH_FILES"]

def SaveRoiDB( path_data, studycase ):
    anotherroute = path.join( path_data, constants.OUT_ROI_DIR )
    cost.Cost_roi( anotherroute, studycase, constants.IMPLEMENTATION_ROI_DB, 'Implementation', '1' )
    cost.Cost_roi( anotherroute, studycase, constants.MAINTENANCE_ROI_DB, 'Maintenance', '2' )
    cost.Cost_roi( anotherroute, studycase, constants.OPPORTUNITY_ROI_DB, 'Opportunity', '3' )
    cost.Cost_roi( anotherroute, studycase, constants.TRANSACTION_ROI_DB,'Transaction', '4' )
    cost.Cost_roi( anotherroute, studycase, constants.PLATFORM_ROI_DB, 'Platform', '5' )
    save.Save_roi( anotherroute, studycase, constants.INTAKE_ROI_DB, 'Cap', '6' )
    save.Save_roi( anotherroute, studycase, constants.PTAP_ROI_DB, 'PTAP', '7' )
    carb.Carb_roi( anotherroute, studycase )
    sens.Sens_roi( anotherroute, studycase )

def CreateZip(path, studyCase_id, user_folder):
    print ("Creating zip file")
    print ("path : %s" % path)
    print ("user_folder : %s" % user_folder)
    print ("studyCase_id : %s" % studyCase_id)
    shutil.make_archive(path,'zip',path)
    print (path)
    url = "%s%s%s"% (constants.ZIP_CREATION_DIR , user_folder , ".zip")
    print ("url  : %s" % url )

    args = [int(studyCase_id),url ]
    print ("before connect ")
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('__wpupdate_download_zip',args)
    conn.commit()
    cursor.close()
    conn.close()
    
    #updateDataDB(args,'__wpupdate_download_zip')
    print ("after callproc")
    return True