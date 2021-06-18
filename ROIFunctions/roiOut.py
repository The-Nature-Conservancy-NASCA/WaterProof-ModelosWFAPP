from os import environ, path
import ROIFunctions.cost as cost
import ROIFunctions.saves as save
import ROIFunctions.sensivity as sens
import ROIFunctions.carbon as carb

ruta = environ["PATH_FILES"]
OUT = 'out'
IMPLEMENTATION = 'Implementación'
MAINTENANCE = 'Mantenimiento'
OPPORTUNITY = 'Oportunidad'
TRANSACTION = 'Transacción'
PLATFORM = 'Plataforma'
INTAKE = 'INTAKE'
PTAP = 'PTAP'
CARBON = 'CARBONO'

def SaveRoiDB( path_data, studycase ):
    anotherroute = path.join( path_data, OUT )
    save.Save_roi( anotherroute, studycase, INTAKE, 'Cap', '6' )
    save.Save_roi( anotherroute, studycase, PTAP, 'PTAP', '7' )
    carb.Carb_roi( anotherroute, studycase )
    sens.Sens_roi( anotherroute, studycase )
    cost.Cost_roi( anotherroute, studycase, IMPLEMENTATION, 'Implementation', '1' )
    cost.Cost_roi( anotherroute, studycase, MAINTENANCE, 'Maintenance', '2' )
    cost.Cost_roi( anotherroute, studycase, OPPORTUNITY, 'Opportunity', '3' )
    cost.Cost_roi( anotherroute, studycase, TRANSACTION,'Transaction', '4' )
    cost.Cost_roi( anotherroute, studycase, PLATFORM, 'Platform', '5' )
