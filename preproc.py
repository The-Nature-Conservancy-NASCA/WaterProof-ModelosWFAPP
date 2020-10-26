# Date: 24/09/2020
# Author: Diego Rodriguez - Skaphe Tecnologia SAS
# WFApp


# Importacion de librerias
import sys
import os.path
from os import path
import fiona
import rasterio
from natcap.invest.hydropower import hydropower_water_yield as awy
from natcap.invest.seasonal_water_yield import seasonal_water_yield as swy
from natcap.invest.sdr import sdr
from natcap.invest.ndr import ndr
from natcap.invest import carbon
from zonalStatistics import calculateRainfallDayMonth,calculateStatistic
from zonalStatistics import saveCsv
from calculateConcentrations import calcConcentrations as cntr
sys.path.append('config')
from config import config
from connect import connect
import datetime
import ogr
import osgeo.osr as osr
from rasterio.mask import mask
import geopandas as gpd


# Exportar cuenca delimitada a shp
def exportToShp(catchment, path):
	params = config(section='postgresql')
	connString = "PG: host=" + params['host'] + " dbname=" + params['database'] + " user=" + params['user'] + " password=" + params['password'] 
	conn=ogr.Open(connString)
	if conn is None:
		print('Could not open a database or GDAL is not correctly installed!')
		sys.exit(1)

	output = os.path.join(path,"in","catchment","catchment.shp")
	source = osr.SpatialReference()
	source.ImportFromEPSG(4326)
	target = osr.SpatialReference()
	target.ImportFromEPSG(3857)
	transform = osr.CoordinateTransformation(source, target)

	# Schema definition of SHP file
	out_driver = ogr.GetDriverByName( 'ESRI Shapefile' )
	out_ds = out_driver.CreateDataSource(output)

	out_layer = out_ds.CreateLayer("catchment", target, ogr.wkbPolygon)
	fd = ogr.FieldDefn('ws_id',ogr.OFTInteger)
	fd1 = ogr.FieldDefn('subws_id',ogr.OFTInteger)
	out_layer.CreateField(fd)
	out_layer.CreateField(fd1)
	if(len(catchment) == 1):
		params = ' = ' + str(catchment[0]) 
	elif(len(catchment) > 1):
		params = ' IN ('
		for c in catchment:
			params = params + str(c) + ','
		params = params[:-1] + ')'



	if(catchment != -1):
		sql = "select * from delineated_catchment where id_delineate_catchment" + str(params)

		# layer = conn.GetLayerByName("delineated_catchment")
		layer = conn.ExecuteSQL(sql)
		
		feat = layer.GetNextFeature()
		while feat is not None:
			featDef = ogr.Feature(out_layer.GetLayerDefn())
			geom = feat.GetGeometryRef()
			geom.Transform(transform)		
			featDef.SetGeometry(geom)			
			featDef.SetField('ws_id',feat.id_delineate_catchment)		
			featDef.SetField('subws_id',feat.id_delineate_catchment)		
			out_layer.CreateFeature(featDef)
			feat.Destroy()
			feat = layer.GetNextFeature()
			

		conn.Destroy()
		out_ds.Destroy()
		
	return os.path.join(os.getcwd(),output)

# Crear directorio para almacenar procesamientos
def createFolder(user,date):
	pathF = 'tmp/' + str(user) + "_" + str(date.year) + "_" + str(date.month) + "_" + str(date.day)
	folders = {
		"in":[
			"catchment",
			"01-INVEST_QUALITY",
			"02-PREPROC_RIOS",
			"03-INVEST",
			"04-RIOS",
			"05-ROI",
			"06-AQUEDUCT"
		],
		"out":[
			"01-INVEST_QUALITY",
			"02-PREPROC_RIOS",
			"03-INVEST",
			"04-RIOS",
			"05-ROI",
			"06-AQUEDUCT"
		]
	}
	isdir = path.isdir(pathF)
	if(not isdir):
		os.mkdir(pathF)

	for key in folders:
		pathNew = os.path.join(pathF,key)
		isdirF = path.isdir(pathNew)
		if(not isdirF):
			os.mkdir(pathNew)
		for item in folders[key]:
			pathNew2 = os.path.join(pathF,key,item)
			isdirFF = path.isdir(pathNew2)
			if(not isdirFF):
				os.mkdir(pathNew2)
	
	return pathF
   
# Cortar raster
def cutRaster(catchment,path,out_path):
	data = rasterio.open(path)
	with fiona.open(catchment, "r") as shapefile:
		shapes = [feature["geometry"] for feature in shapefile]
	
	with rasterio.open(path) as src:
		out_image, out_transform = mask(src, shapes, crop=True)
		out_meta = src.meta

	out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
	
	with rasterio.open(os.path.join(out_path,os.path.basename(path)), "w", **out_meta) as dest:
		dest.write(out_image)

	return os.path.join(out_path,os.path.basename(path))

# Recuperar macroregion por id
def getRegionFromId(basin):
	result = ''
	cursor = connect('postgresql').cursor()
	cursor.callproc('getBasin',[basin])
	result = cursor.fetchall()
	for row in result:
		result = row
	cursor.close()
	return result
 
# Recuperar constante por macroregion
def getConstantFromBasin(basin,constantName):
	result = ''
	cursor = connect('postgresql_alfa').cursor()
	cursor.callproc('wfa.getconstant',[basin,constantName])
	result = cursor.fetchall()
	for row in result:
		result = row
	cursor.close()
	return result

# Obtener parametros de modelo
def getParameters(basin,model):
	result = ''
	listResult = []
	cursor = connect('postgresql_alfa').cursor()
	cursor.callproc('wfa.getparametersmodel',[basin,model])
	result = cursor.fetchall()
	for row in result:
		listResult.append(row)
	cursor.close()
	return listResult

# Evaluar si existen las ejecuciones realizadas para AWY, SDR y NDR para calcular concentraciones
def verifyExec(path):
	pathWs = os.path.join(path,"out","01-INVEST_QUALITY")
	execute = True
	execList = []
	execList.append("AWY")
	execList.append("SDR")
	execList.append("NDR")

	for item in execList:
		pathNew = os.path.join(pathWs,item)
		isdir = os.path.isdir(pathNew)
		if(not isdir):
			execute = False
			break

	return execute
 
# Ejecutar calculo de concentraciones
def calcConc(execute,path,label,cont):
	pathWs = os.path.join(path,"out")
	if(execute):
		s,n,p = cntr(pathWs,label,cont)
	else:
		s,n,p = [-1,-1,-1]

	return s,n,p
 
#Calcular sumatoria de resultado de carbon
def calculateCarbonSum(catchment,path,label):
	stats = ['sum']
	raster = os.path.join(path,'out','01-INVEST_QUALITY','CARBON','tot_c_cur_' + label + '.tif')
	statCalc = calculateStatistic(stats,raster,catchment)
	return statCalc
 
# Procesar parametros
def processParameters(parametersList, basin, catchment,pathF,type,model):
	dictParameters = dict()
	out_path = ""
	in_path = ""
	out_folder = parametersList[0][9]
	out_folder_quality = parametersList[0][10]
	print(out_folder)
	print(out_folder_quality)
	if(type == "quality" or type == "currentCarbon"):
		out_path = os.path.join(os.getcwd(),pathF,'out',out_folder_quality)
		in_path = os.path.join(os.getcwd(),pathF,'in',out_folder_quality)
	else:
		out_path = os.path.join(os.getcwd(),pathF,'out',out_folder)
		in_path = os.path.join(os.getcwd(),pathF,'in',out_folder)
	

	isdir = os.path.isdir(out_path)
	if(not isdir):
		os.mkdir(out_path)

	isdir = os.path.isdir(in_path)
	if(not isdir):
		os.mkdir(in_path)

	for parameter in parametersList:
		name = parameter[0]
		value = parameter[1]
		if(value == 'False'):
			value = False
		elif(value == 'True'):
			value = True		
		cut = parameter[2]
		constant = parameter[3]
		suffix = parameter[4]
		empty = parameter[5]
		file = parameter[6]
		folder = parameter[7]
		outPathType = parameter[8]
		calculado = parameter[11]
		if(suffix):
			region = getRegionFromId(basin)
			label = region[4]
			value = label
		if(constant):
			constantValue = getConstantFromBasin(basin,name)
			value = constantValue[2]
		if(empty):
			value = ''
		if(cut and model == 'carbon'):
			value = cutRaster(catchment,value,in_path)
		if(file):
			value = catchment
		if(outPathType):
			value = out_path
		if(calculado):
			region = getRegionFromId(basin)
			label = region[4]
			rainfallList = calculateRainfallDayMonth(value,catchment,label)
			saveCsv(['month','events'],rainfallList,in_path)
			value = os.path.join(in_path,"rainfall_day.csv")
		dictParameters[name] = value
	return dictParameters,out_path,label

def executeFunction(basin,model,type,id_catchment,id_usuario):
	date = datetime.date.today()
	path = createFolder(id_usuario,date)

	list = getParameters(basin,model)	
	catchment = exportToShp(id_catchment, path)
	parameters,pathF,label = processParameters(list,basin,catchment,path,type,model)
	

	if(model == 'awy'):
		awy.execute(parameters)
	elif(model == 'sdr'):
		sdr.execute(parameters)
	elif(model == 'carbon'):
		carbon.execute(parameters)
	elif(model == 'ndr'):
		ndr.execute(parameters)
	elif(model == 'swy'):
		swy.execute(parameters)

	return catchment,path,label

#date = datetime.date.today()
#path = createFolder(1,date)
#catchment = exportToShp(2, path)
#list = getParameters(44,'carbon')
#dict,pathF,label = processParameters(list,44,catchment,path,True)
#executeFunction(dict,'carbon')
#execute = verifyExec(path)
#s,n,p = calcConc(execute,path,label)
#print(s,n,p)
#calculateCarbonSum(catchment,path,label)
#cutRaster('aaaaa',dict)