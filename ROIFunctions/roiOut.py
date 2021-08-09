from os import environ, path
import shutil,os
import ROIFunctions.cost as cost
import ROIFunctions.saves as save
import ROIFunctions.sensivity as sens
import ROIFunctions.carbon as carb
import constants 
from ROIFunctions.common_functions import updateDataDB

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
    shutil.make_archive(path,'zip',path)
    print (path)
    link= (constants.ZIP_CREATION_DIR + user_folder + ".zip")
    args = [studyCase_id,link]
    updateDataDB(args,'__wpupdate_download_zip')
    