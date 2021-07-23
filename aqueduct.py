import os, ogr, sys, osr
import geopandas as gpd
sys.path.append('config')
from ROIFunctions.common_functions import insertParameter,selectDataDB
from connect import connect

ruta = os.environ["PATH_FILES"]

# Exportar cuenca delimitada a shp
def cutShp(catchment, layer, out):
    # print(layer)
    # print(layer)
    # print(catchment)
    # inLayer = gpd.read_file(layer)
    # clipLayer = gpd.read_file(catchment)
    # # # ly_sindexed = inLayer
    # # # zclip_sindexed = clipLayer
    # # # ly_sindexed.sindex
    # # # zclip_sindexed.sindex

    # result_clip = gpd.clip(inLayer,clipLayer)
    # result_clip.to_file(out)

    # print(layer)
    # print(out)
    # print(catchment)

    ## Input
    driverName = "ESRI Shapefile"
    driver = ogr.GetDriverByName(driverName)
    inDataSource = driver.Open(layer)
    inLayer = inDataSource.GetLayer()

    sourceprj = inLayer.GetSpatialRef()
    
    # print("src: " + str(sourceprj))
    
    # targetprj.ImportFromEPSG(54004)
    # transform = osr.CoordinateTransformation(sourceprj, targetprj)


    # print("in:" + str(inLayer.GetFeatureCount()))
    ## Clip
    inClipSource = driver.Open(catchment)
    inClipLayer = inClipSource.GetLayer()
    # print("clip:" + str(inClipLayer.GetFeatureCount()))
    targetprj = inClipLayer.GetSpatialRef()
    # print("target: " + str(targetprj))

    ## Clipped Shapefile... Maybe??? 
    outDataSource = driver.CreateDataSource(out)
    outLayer = outDataSource.CreateLayer('FINAL', geom_type=ogr.wkbPolygon)

    ogr.Layer.Clip(inLayer, inClipLayer, outLayer)
    # print("out:" + str(outLayer.GetFeatureCount()))
    inDataSource.Destroy()
    inClipSource.Destroy()
    outDataSource.Destroy()
	
    # ## Input
    # driverName = "ESRI Shapefile"
    # driver = ogr.GetDriverByName(driverName)
    # inDataSource = driver.Open(layer, 0)
    # inLayer = inDataSource.GetLayer()

    # memory_driver = ogr.GetDriverByName('memory')
    # memory_ds = memory_driver.CreateDataSource('temp')
    # buff_lyr = memory_ds.CreateLayer('buffer')
    # buff_feat = ogr.Feature(buff_lyr.GetLayerDefn())
    

    # for f in inLayer:
    #     print(f.geometry)
    #     buff_geom = f.geometry().Buffer(0)
    #     tmp = buff_feat.SetGeometry(buff_geom)
    #     tmp = buff_lyr.CreateFeature(buff_feat)

    # ## Clip layer
    # inClip = driver.Open(catchment, 0)
    # inClipLayer = inClip.GetLayer()

    # ## Clipped Shapefile... Maybe??? 
    # outDataSource = driver.CreateDataSource(out)
    # outLayer = outDataSource.CreateLayer('FINAL', geom_type=ogr.wkbPolygon)



    # ogr.Layer.Clip(inLayer, inClipLayer, buff_lyr)
    # inDataSource.Destroy()
    # inClip.Destroy()
    # outDataSource.Destroy()

# Recuperar constante por macroregion
def getpath(basin,constantName):
	result = ''
	cursor = connect('postgresql_alfa').cursor()
	cursor.callproc('__wp_getpathbasinparameter',[basin,constantName])
	result = cursor.fetchall()
	for row in result:
		result = row[0]
	cursor.close()
	return result

def cutAqueduct(path):
    path_catchment = os.path.join(path,'in','catchment','catchment.shp')
    path_out = os.path.join(path,'in','06-AQUEDUCT')
    path_out_f = os.path.join(path,'in')

    isdir = os.path.isdir(path_out_f)
    if(not isdir):
        os.mkdir(path_out_f)

    isdir = os.path.isdir(path_out)
    if(not isdir):
        os.mkdir(path_out)

    listIn = []
    
    listIn.append(getpath(44,49))
    listIn.append(getpath(44,48))

    resultado = dict()


    for item in listIn:        
        cutShp(path_catchment,item,os.path.join(path_out,os.path.basename(item)))
        areaTotal = calculateArea(os.path.join(path_out,os.path.basename(item)))
        if("Historic" in item):
            qan,qanLbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"bws_cat",areaTotal)
            qal,qalLbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"bwd_cat",areaTotal)
            rrr,rrrLbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"iav_cat",areaTotal)
            sev,sevLbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"sev_cat",areaTotal)
            gtd,gtdLbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"gtd_cat",areaTotal)
            rfr,rfrLbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"rfr_cat",areaTotal)
            cfr,cfrLbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"cfr_cat",areaTotal)
            drr,drrLbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"drr_cat",areaTotal)
            ucw,ucwLbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"ucw_cat",areaTotal)
            cep,cepLbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"cep_cat",areaTotal)
            udw,udwLbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"udw_cat",areaTotal)
            usa,usaLbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"usa_cat",areaTotal)
            rri,rriLbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"rri_cat",areaTotal)
            resultado["historic"] = {}
            resultado["historic"]["bws"] = {}
            resultado["historic"]["bws"]["value"] = qan
            resultado["historic"]["bws"]["lbl"] = qanLbl
            resultado["historic"]["bwd"] = {}
            resultado["historic"]["bwd"]["value"] = qal
            resultado["historic"]["bwd"]["lbl"] = qalLbl
            resultado["historic"]["iav"] = {}
            resultado["historic"]["iav"]["value"] = rrr
            resultado["historic"]["iav"]["lbl"] = rrrLbl
            resultado["historic"]["sev"] = {}
            resultado["historic"]["sev"]["value"] = sev
            resultado["historic"]["sev"]["lbl"] = sevLbl
            resultado["historic"]["gtd"] = {}
            resultado["historic"]["gtd"]["value"] = gtd
            resultado["historic"]["gtd"]["lbl"] = gtdLbl
            resultado["historic"]["rfr"] = {}
            resultado["historic"]["rfr"]["value"] = rfr
            resultado["historic"]["rfr"]["lbl"] = rfrLbl
            resultado["historic"]["cfr"] = {}
            resultado["historic"]["cfr"]["value"] = cfr
            resultado["historic"]["cfr"]["lbl"] = cfrLbl
            resultado["historic"]["drr"] = {}
            resultado["historic"]["drr"]["value"] = drr
            resultado["historic"]["drr"]["lbl"] = drrLbl
            resultado["historic"]["ucw"] = {}
            resultado["historic"]["ucw"]["value"] = ucw
            resultado["historic"]["ucw"]["lbl"] = ucwLbl
            resultado["historic"]["cep"] = {}
            resultado["historic"]["cep"]["value"] = cep
            resultado["historic"]["cep"]["lbl"] = cepLbl
            resultado["historic"]["udw"] = {}
            resultado["historic"]["udw"]["value"] = udw
            resultado["historic"]["udw"]["lbl"] = udwLbl
            resultado["historic"]["usa"] = {}
            resultado["historic"]["usa"]["value"] = usa
            resultado["historic"]["usa"]["lbl"] = usaLbl
            resultado["historic"]["rri"] = {}
            resultado["historic"]["rri"]["value"] = rri
            resultado["historic"]["rri"]["lbl"] = rriLbl
            # print("Physical, Quantity: " + str(qan) + "/" + qanLbl)
            # print("Physical, Quality: " + str(qal) + "/" + qalLbl)
            # print("Regulatory & reputation: " + str(rrr) + "/" + rrrLbl)
        elif("Future" in item):
            ws10,ws10Lbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"ws3028tr",areaTotal)
            sv10,sv10Lbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"sv3028tr",areaTotal)
            ut10,ut10Lbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"ut3028tr",areaTotal)
            bt10,bt10Lbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"bt3028tr",areaTotal)
            ws20,ws20Lbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"ws4028tr",areaTotal)
            sv20,sv20Lbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"sv4028tr",areaTotal)
            ut20,ut20Lbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"ut4028tr",areaTotal)
            bt20,bt20Lbl = calculateIndex(os.path.join(path_out,os.path.basename(item)),"bt4028tr",areaTotal)
            resultado["future10"] = {}
            resultado["future10"]["ws"] = {}
            resultado["future10"]["ws"]["value"] = ws10
            resultado["future10"]["ws"]["lbl"] = ws10Lbl
            resultado["future10"]["sv"] = {}
            resultado["future10"]["sv"]["value"] = sv10
            resultado["future10"]["sv"]["lbl"] = sv10Lbl
            resultado["future10"]["ut"] = {}
            resultado["future10"]["ut"]["value"] = ut10
            resultado["future10"]["ut"]["lbl"] = ut10Lbl
            resultado["future10"]["bt"] = {}
            resultado["future10"]["bt"]["value"] = bt10
            resultado["future10"]["bt"]["lbl"] = bt10Lbl
            resultado["future20"] = {}
            resultado["future20"]["ws"] = {}
            resultado["future20"]["ws"]["value"] = ws20
            resultado["future20"]["ws"]["lbl"] = ws20Lbl
            resultado["future20"]["sv"] = {}
            resultado["future20"]["sv"]["value"] = sv20
            resultado["future20"]["sv"]["lbl"] = sv20Lbl
            resultado["future20"]["ut"] = {}
            resultado["future20"]["ut"]["value"] = ut20
            resultado["future20"]["ut"]["lbl"] = ut20Lbl
            resultado["future20"]["bt"] = {}
            resultado["future20"]["bt"]["value"] = bt20
            resultado["future20"]["bt"]["lbl"] = bt20Lbl
            # print("Water Stress: " + str(ws20) + "/" + ws20Lbl)
            # print("Water Supply: " + str(bt20) + "/" + bt20Lbl)
            # print("Water Demand: " + str(ut20) + "/" + ut20Lbl)
            # print("Season Variablity: " + str(sv20) + "/" + sv20Lbl)

    return resultado       

def calculateArea(shp):
    driverName = "ESRI Shapefile"
    driver = ogr.GetDriverByName(driverName)
    inDataSource = driver.Open(shp,1)
    inLayer = inDataSource.GetLayer()
    new_field = ogr.FieldDefn("Area", ogr.OFTReal)
    new_field.SetWidth(32)
    new_field.SetPrecision(2) #added line to set precision
    inLayer.CreateField(new_field)
    areaT = 0

    for feature in inLayer:
        geom = feature.GetGeometryRef()
        area = geom.GetArea() 
        areaT = areaT + area
        feature.SetField("Area", area)
        inLayer.SetFeature(feature)

    return areaT

def calculateIndex(shp,idx, areaT):
    driverName = "ESRI Shapefile"
    driver = ogr.GetDriverByName(driverName)
    inDataSource = driver.Open(shp,1)
    inLayer = inDataSource.GetLayer()
    idxSum = 0

    for feature in inLayer:
        idxValue = feature.GetField(idx)
        area = feature.GetField("Area")
        idxSum = idxSum + (area*idxValue)

    resultado = idxSum/areaT
    roundResultado = round(resultado)
    print(roundResultado)
    switcher = {
        0: "No hay datos",
        1: "Bajo",
        2: "Bajo-Medio",
        3: "Medio-Alto",
        4: "Alto",
        5: "Muy Alto"
    }
    print(roundResultado)

    lvl = switcher[roundResultado]

    return roundResultado, lvl

def insertResults(result,id_intake):

    count = selectDataDB('Select count(*) from public.waterproof_reports_aqueduct where intake_id = '+id_intake)
    if( count[0] == 0 ):
        # Future 10 Years
        future10 = result['future10']
        for key in future10:
            args=[id_intake,'Future 10 Years',str('F_10_'+key.upper()),future10[key]['value']]
            insertParameter('__wp_aqueduct_insert',args)

        # Future 20 years
        future20 = result['future20']
        for key in future20:
            args=[id_intake,'Future 20 Years',f'F_20_{key.upper()}',future20[key]['value']]
            insertParameter('__wp_aqueduct_insert',args)

        # HISTORIC
        historic = result['historic']
        for key in historic:
            if('bws' in key or 'bwd' in key or 'iav' in key or 'sev' in key or 'gtd' in key or 'rfr' in key or 'cfr' in key):
                args=[id_intake,'Physical Risk associated with Amount of Water','H_'+key.upper(),historic[key]['value']]
                insertParameter('__wp_aqueduct_insert',args)
            if('ucw' in key or 'cep' in key or 'udw' in key or 'usa' in key or 'rri' in key):
                args=[id_intake,'Physical Risk quantity',f'H_{key.upper()}',historic[key]['value']]
                insertParameter('__wp_aqueduct_insert',args)
            if('drr' in key ):
                args=[id_intake,'Regulatory and reputational',f'H_{key.upper()}',historic[key]['value']]
                insertParameter('__wp_aqueduct_insert',args)



catchment = '/home/skaphe/Documentos/tnc/modelos/Workspace_BasinDelineation/tmp/9_2020_10_10/in/catchment/catchment.shp'
layer = '/home/skaphe/Documentos/tnc/modelos/entradas/16-Aqueduct/Future_Index.shp'
# cutAqueduct('9','2020_10_13')