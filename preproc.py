# Date: 24/09/2020
# Author: Diego Rodriguez - Skaphe Tecnologia SAS
# WFApp


# Importacion de librerias
import sys
import os.path
from os import path, environ
import pathlib
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
from createBioParamCsv import getColsParams,generateCsv, getBiophysicParams
sys.path.append('config')
from config import config
from connect import connect
import datetime
import ogr
import osgeo.osr as osr
from rasterio.mask import mask
import geopandas as gpd
import AdvancedHTMLParser
import requests
from AdvancedHTMLParser import AdvancedTag
from Disaggregation_WaterFunds.Disaggregation_and_Convolution import Desaggregation_BaU_NBS
from ROI_WaterFunds.ROI import ROI_Analisys
import logging
import json

logger = logging.getLogger(__name__) # grabs underlying WSGI logger
logger.setLevel(logging.INFO)

ruta = environ["PATH_FILES"]

# Exportar cuenca delimitada a shp
def exportToShp(catchment, path):
	params = config(section='postgresql_alfa')
	connString = "PG: host=" + params['host'] + " dbname=" + params['database'] + " user=" + params['user'] + " password=" + params['password'] 
	conn=ogr.Open(connString)
	if conn is None:
		print('Could not open a database or GDAL is not correctly installed!')
		sys.exit(1)

	output = os.path.join(path,"in","catchment","catchment.shp")
	source = osr.SpatialReference()
	epsg_4326 = 4326
	source.ImportFromEPSG(epsg_4326)
	target = osr.SpatialReference()
	# epsg_3857 = 3857
	epsg_54004 = 54004
	target.ImportFromEPSG(epsg_54004)
	transform = osr.CoordinateTransformation(source, target)

	# Schema definition of SHP file
	out_driver = ogr.GetDriverByName('ESRI Shapefile')
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
		sql = "select * from waterproof_intake_polygon where delimitation_type = 'SBN' and intake_id" + str(params)

		# layer = conn.GetLayerByName("delineated_catchment")
		layer = conn.ExecuteSQL(sql)
		
		feat = layer.GetNextFeature()
		while feat is not None:
			featDef = ogr.Feature(out_layer.GetLayerDefn())
			geom = feat.GetGeometryRef()
			geom.Transform(transform)		
			featDef.SetGeometry(geom)			
			featDef.SetField('ws_id',feat.id)		
			featDef.SetField('subws_id',feat.id)		
			out_layer.CreateFeature(featDef)
			feat.Destroy()
			feat = layer.GetNextFeature()
			

		conn.Destroy()
		out_ds.Destroy()
		
	return os.path.join(os.getcwd(),output)

# Crear directorio para almacenar procesamientos
def createFolder(user,date):
	pathF = path.join(ruta,"salidas",str(user) + "_" + str(date.year) + "_" + str(date.month) + "_" + str(date.day))
	# pathF = ruta + str(user) + "_" + str(date.year) + "_" + str(date.month) + "_" + str(date.day)
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
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	cursor.callproc('__wp_getBasin',[basin])
	result = cursor.fetchall()
	for row in result:
		result = row
	cursor.close()
	conn.close()
	return result
 
# Recuperar constante por macroregion
def getConstantFromBasin(basin,constantName):
	result = ''
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	cursor.callproc('__wp_getconstant',[basin,constantName])
	result = cursor.fetchall()
	for row in result:
		result = row
	cursor.close()
	conn.close()
	return result

# Obtener parametros de modelo
def getParameters(basin,model):
	result = ''
	listResult = []
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	cursor.callproc('__wp_getparametersmodel',[basin,model])
	result = cursor.fetchall()
	for row in result:
		listResult.append(row)
	cursor.close()
	conn.close()
	return listResult

# Obtener parametros de modelo
def InsertQualityParameters(catchment,element,awy,wsed,wn,wp,csed,cn,cp):
	listResult = []
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	cursor.callproc('__wp_insertConcentrationsInVEST',[catchment,element,awy,wsed,wn,wp,csed,cn,cp])
	conn.commit()
	cursor.close()
	conn.close()

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
		s,n,p,q,sW,nW,pW = cntr(pathWs,label,cont)
	else:
		s,n,p,q,sW,nW,pW = [-1,-1,-1,-1,-1,-1,-1]

	return s,n,p,q,sW,nW,pW
 
#Calcular sumatoria de resultado de carbon
def calculateCarbonSum(catchment,path,label):
	stats = ['sum']
	raster = os.path.join(path,'out','01-INVEST_QUALITY','CARBON','tot_c_cur_' + label + '.tif')
	statCalc = calculateStatistic(stats,raster,catchment)
	return statCalc

def getPathsClimateValueFromStudyCaseId(id):
	listResult = []
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	cursor.callproc('__wpget_paths_climate_value',[id])
	result = cursor.fetchall()
	for row in result:
		listResult.append(row)
	cursor.close()
	conn.close()
	return listResult

# Procesar parametros
def processParameters(parametersList, basin, catchment, pathF, type, model, user, year, id_case):
	dictParameters = dict()
	out_path = ""
	in_path = ""
	out_folder = parametersList[0][9]
	out_folder_quality = parametersList[0][10]
	print("processParameters :: outFolder :: {%s}" % {out_folder})
	print("processParameters :: out_folder_quality :: {%s}" % {out_folder_quality})
	
	if(type == "quality" or type == "currentCarbon"):
		out_path = os.path.join(os.getcwd(),pathF,'out',out_folder_quality)
		in_path = os.path.join(os.getcwd(),pathF,'in',out_folder_quality)
	else:
		out_path = os.path.join(os.getcwd(),pathF,'out',out_folder, 'YEAR_' + str(year))
		in_path = os.path.join(os.getcwd(),pathF,'in',out_folder)
	

	isdir = os.path.isdir(out_path)
	if(not isdir):
		os.mkdir(out_path)

	isdir = os.path.isdir(in_path)
	if(not isdir):
		os.mkdir(in_path)

	default_year = "YEAR_0"
	year_dir = "/YEAR_{}/".format(year)

	paths_climate_value = getPathsClimateValueFromStudyCaseId(id_case)
	erosivity_path_cv = ''
	eto_path_cv = ''
	precipitation_path_cv = ''
	
	PRECIPITATION = '01-Precipitation'
	EVAPOTRANSPIRATION = '02-Evapotranspiration'
	RAINFALL_EROSIVITY = '06-Rainfall_Erosivity'
	
	EROSIVITY_PATH = 'erosivity_path'
	ETO_PATH = 'eto_path'
	PRECIPITATION_PATH = 'precipitation_path'

	if (len(paths_climate_value) > 0):
		for p in paths_climate_value:
			path = p[2]
			if (PRECIPITATION in path):
				precipitation_path_cv = path
			elif (EVAPOTRANSPIRATION in path):
				eto_path_cv = path
			elif (RAINFALL_EROSIVITY in path):
				erosivity_path_cv = path	
	
	for parameter in parametersList:
		name = parameter[0]
		value = parameter[1]
		if default_year in value:
			value = value.replace(default_year, year_dir)

		if (name == PRECIPITATION_PATH and precipitation_path_cv != ''):
			value = precipitation_path_cv

		if (name == ETO_PATH and eto_path_cv != ''):
			value = eto_path_cv

		if (name == EROSIVITY_PATH and erosivity_path_cv != ''):
			value = erosivity_path_cv

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
		bio_param = parameter[13]
		
		if(suffix):
			region = getRegionFromId(basin)
			label = region[4]
			value = label
		if(constant):
			if (name == 'k_param' and model == 'ndr'):
				constantValue = getConstantFromBasin(basin,'k_param_ndr')
			elif(name == 'k_param' and model == 'sdr'):
				constantValue = getConstantFromBasin(basin,'k_param_sdr')
			else:
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
		if(bio_param):
			region = getRegionFromId(basin)
			label = region[4]
			file = os.path.join(os.getcwd(),pathF,'in',"biophysical_table.csv")
			# values,headers = getColsParams("apps.skaphe.com",27017,"waterProof","parametros_biofisicos",user,label,True)
			default = 'y'
			values, headers = getBiophysicParams(user, label, default)
			generateCsv(headers,values,file)
			value = file
		dictParameters[name] = value
	return dictParameters,out_path,label

def executeFunction(basin,model,type,id_catchment,id_usuario, year, id_case):
	logger.info("execFunction :: start")
	print(":: execFunction :: start")
	date = datetime.date.today()
	path = createFolder(id_usuario,date)

	list = getParameters(basin,model)	
	catchment = exportToShp(id_catchment, path)
	parameters,pathF,label = processParameters(list,basin,catchment,path,type,model,id_usuario, year, id_case)
	json_parameters = json.dumps(parameters, indent=2)
	print("writing file %s/parameters_.json" % (path))
	txt_file = open(os.path.join(path,"parameters_" + model + ".json"), "w")
	txt_file.write(json_parameters)
	txt_file.close()
	# print(json.dumps(parameters, indent=2))

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


""" Function to get the areas from IPO (Invest Portfolio)"""
""" using AdvancedHTMLParser return all the elements with className = budget_totals """
""" then return an array of all areas except the sum of all areas (All Years).  """
""" This area is the first element """
def parse_html_to_get_areas(path_file):
    #path_file = 'C:/tmp/TNC/ipa_report_Dummy.html' 
    class_name = "budget_totals"
    f = open(path_file, 'r')
    html = f.read()
    parser = AdvancedHTMLParser.AdvancedHTMLParser()
    parser.parseStr(html)
    budget_totals = parser.getElementsByClassName(class_name)
    areas = {}
    i = 0
    for t in budget_totals:
        if (i > 0):
            areas['area_' + str(i)] = float(t.getChildren()[3].innerText)
        i = i + 1
        #areas.append(float(t.getChildren()[3].innerText))
    #areas.pop(0)
    return areas


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

def processDissagregation(user_id, study_cases_id):
	
	print ("processDissagregation")
	dict_result = {}

	query = {'type':'quality', 'id_usuario':'1', 'basin' : '44', 'models' : 'sdr', 'catchment' : '1', 'models' : 'amy', 'models' : 'ndr'}
	print (query)
	
	api_url = "http://dev.skaphe.com:8000/execInvest"
	response = requests.get(api_url, params=query)

	invest_json = response.json()["resultado"]
	input_invest = []
	input_invest.append({
		'scenario' : 'current',
		'awy' : invest_json[0]['awy'],
		'wsed':invest_json[0]['w']['sediment'],
		'wn':invest_json[0]['w']['nitrogen'],
		'wp':invest_json[0]['w']['phosporus'],
		'bf':0,
		'wc':0,
	})

	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	cursor.callproc('__wpget_nbs_data',[study_cases_id])
	result = cursor.fetchall()

	path_file = '/app/ipa_report_Dummy.html'
	areas = parse_html_to_get_areas(path_file)
	input_nbs = []
	in_time = 0
	for row in result:
		r = {'nbs_name': row[0], 'time_max_benefit': row[1], 'benefit_t0': row[2]}
		d = {**r, **areas}
		in_time = row[3]
		input_nbs.append(d)

	dict_result["input_invest"] = input_invest
	dict_result["input_nbs"] = input_nbs
	dict_result["time"] = in_time
	return dict_result

def processRoi(user_id, study_cases_id):
	print ("processRoi")
	current_dir = pathlib.Path().absolute()
	demo_data = "/ROI_WaterFunds/Project"
	path_data = str(current_dir) + demo_data
	print ("processROI :: path_data :: " + path_data)
	
	return ROI_Analisys(path_data)


def analysisPeriodFromStudyCase(id):
	print("analysisPeriodFromStudyCase - id::%s" % id)
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	sql = "select analysis_period_value from public.waterproof_study_cases_studycases where id = %s" % id
	cursor.execute(sql)
	year = 1
	try:
		row = cursor.fetchone()
		year = row[0]
	except:
		year=-1
	return year