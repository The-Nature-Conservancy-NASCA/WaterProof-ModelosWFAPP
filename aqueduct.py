import os, ogr, sys
import geopandas as gpd
sys.path.append('config')
from connect import connect

# Exportar cuenca delimitada a shp
def cutShp(catchment, layer, out):
    print(layer)

    inLayer = gpd.read_file(layer)
    clipLayer = gpd.read_file(catchment)
    ly_sindexed = inLayer
    zclip_sindexed = clipLayer
    ly_sindexed.sindex
    zclip_sindexed.sindex

    result_clip = gpd.clip(ly_sindexed,zclip_sindexed)
    result_clip.to_file(out)


	
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
	cursor.callproc('wfa.getpathbasinparameter',[basin,constantName])
	result = cursor.fetchall()
	for row in result:
		result = row[0]
	cursor.close()
	return result

def cutAqueduct(usuario,fecha):
    path = os.path.join(os.getcwd(),'tmp',usuario + '_' + fecha)
    path_catchment = os.path.join(path,'in','catchment','catchment.shp')
    path_out = os.path.join(path,'in','06-AQUEDUCT')
    listIn = []
    listIn.append(getpath(44,48))
    listIn.append(getpath(44,49))

    for item in listIn:        
        cutShp(path_catchment,item,os.path.join(path_out,os.path.basename(item)))



catchment = '/home/skaphe/Documentos/tnc/modelos/Workspace_BasinDelineation/tmp/9_2020_10_10/in/catchment/catchment.shp'
layer = '/home/skaphe/Documentos/tnc/modelos/entradas/16-Aqueduct/Future_Index.shp'
cutAqueduct('9','2020_10_13')