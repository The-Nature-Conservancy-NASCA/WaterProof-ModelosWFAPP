from os import environ, path
import ROIFunctions.cost as cost
import ROIFunctions.saves as save
import ROIFunctions.sensivity as sens
import ROIFunctions.carbon as carb
import constants

ruta = environ["PATH_FILES"]

def SaveRoiDB( path_data, studycase ):
    anotherroute = path.join( path_data, OUT_ROI_DIR )
    cost.Cost_roi( anotherroute, studycase, IMPLEMENTATION_ROI_DB, 'Implementation', '1' )
    cost.Cost_roi( anotherroute, studycase, MAINTENANCE_ROI_DB, 'Maintenance', '2' )
    cost.Cost_roi( anotherroute, studycase, OPPORTUNITY_ROI_DB, 'Opportunity', '3' )
    cost.Cost_roi( anotherroute, studycase, TRANSACTION_ROI_DB,'Transaction', '4' )
    cost.Cost_roi( anotherroute, studycase, PLATFORM_ROI_DB, 'Platform', '5' )
    save.Save_roi( anotherroute, studycase, INTAKE_ROI_DB, 'Cap', '6' )
    save.Save_roi( anotherroute, studycase, PTAP_ROI_DB, 'PTAP', '7' )
    carb.Carb_roi( anotherroute, studycase )
    sens.Sens_roi( anotherroute, studycase )
