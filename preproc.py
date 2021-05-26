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
from createBioParamCsv import generateCsv, getDefaultBiophysicParams, getUserBiophysicParams
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
import re
import math

logger = logging.getLogger(__name__) # grabs underlying WSGI logger
logger.setLevel(logging.INFO)

base_path = environ["PATH_FILES"]

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
def createFolder(user, id_case, date):
	usr_folder = "%s_%s_%s-%s-%s" % (user,id_case, date.year, date.month, date.day)
	out_folder = path.join(base_path,"out", usr_folder)
	
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
	isdir = path.isdir(out_folder)
	if(not isdir):
		os.mkdir(out_folder)

	for key in folders:
		pathNew = os.path.join(out_folder,key)
		isdirF = path.isdir(pathNew)
		if(not isdirF):
			os.mkdir(pathNew)
		for item in folders[key]:
			pathNew2 = os.path.join(out_folder,key,item)
			isdirFF = path.isdir(pathNew2)
			if(not isdirFF):
				os.mkdir(pathNew2)
	
	return out_folder
   
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

# Insert Quqlity Parameters
def InsertQualityParameters(catchment,element,awy,wsed,wn,wp,csed,cn,cp):
	listResult = []
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	cursor.callproc('__wp_insertConcentrationsInVEST',[catchment,element,awy,wsed,wn,wp,csed,cn,cp])
	conn.commit()
	cursor.close()
	conn.close()

# Evaluar si existen las ejecuciones realizadas para AWY, SDR y NDR para calcular concentraciones
def verifyExec(path, sub_dir):
	#sub_dir = "01-INVEST_QUALITY"
	pathWs = os.path.join(path,"out",sub_dir)
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
def calcConc(execute,path,label,cont, sub_dir, year_dir):
	pathWs = os.path.join(path,"out")
	if(execute):
		s,n,p,q,sW,nW,pW,bf = cntr(pathWs,label,cont, sub_dir, year_dir)
	else:
		s,n,p,q,sW,nW,pW,bf = [-1,-1,-1,-1,-1,-1,-1,-1]

	return s,n,p,q,sW,nW,pW,bf
 
#Calcular sumatoria de resultado de carbon
def calculateCarbonSum(catchment,path,label, model_dir, year_dir):
	stats = ['sum']
	#model_dir = '01-INVEST_QUALITY'
	raster = os.path.join(path,'out',model_dir,'CARBON', year_dir,'tot_c_cur_' + label + '.tif')
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
def processParameters(parametersList, basin, catchment, pathF, type, model, user, year, id_case, id_catchment):
	dictParameters = dict()
	out_path = ""
	in_path = ""
	out_folder = parametersList[0][9]
	out_folder_quality = parametersList[0][10]
	print("processParameters :: outFolder :: {%s}" % {out_folder})
	print("processParameters :: out_folder_quality :: {%s}" % {out_folder_quality})	
	
	erosivity_path_cv = ''
	eto_path_cv = ''
	precipitation_path_cv = ''

	PRECIPITATION = '01-Precipitation'
	EVAPOTRANSPIRATION = '02-Evapotranspiration'
	RAINFALL_EROSIVITY = '06-Rainfall_Erosivity'
	
	EROSIVITY_PATH = 'erosivity_path'
	ETO_PATH = 'eto_path'
	PRECIPITATION_PATH = 'precipitation_path'

	PRECIPITATION_DIR = 'precip_dir'
	ET0_DIR = 'et0_dir'

	if(type == "quality" or type == "currentCarbon"):
		out_path = os.path.join(os.getcwd(),pathF,'out',out_folder_quality)
		isdir = os.path.isdir(out_path)
		if(not isdir):
			os.mkdir(out_path)
		out_path = os.path.join(os.getcwd(),pathF,'out',out_folder_quality, 'YEAR_' + str(year))	
		in_path = os.path.join(os.getcwd(),pathF,'in',out_folder_quality)
	else:
		out_path = os.path.join(os.getcwd(),pathF,'out',out_folder)
		isdir = os.path.isdir(out_path)
		if(not isdir):
			os.mkdir(out_path)
		out_path = os.path.join(os.getcwd(),pathF,'out',out_folder, 'YEAR_' + str(year))
		in_path = os.path.join(os.getcwd(),pathF,'in',out_folder)

		if (type != "current"):
			paths_climate_value = getPathsClimateValueFromStudyCaseId(id_case)

			if (len(paths_climate_value) > 0):
				for p in paths_climate_value:
					path = p[2]
					if (PRECIPITATION in path):
						print("Using Climate Value PATH for: %s" % PRECIPITATION)
						precipitation_path_cv = path
					elif (EVAPOTRANSPIRATION in path):
						eto_path_cv = path
						print("Using Climate Value PATH for: %s" % EVAPOTRANSPIRATION)
					elif (RAINFALL_EROSIVITY in path):
						print("Using Climate Value PATH for: %s" % RAINFALL_EROSIVITY)
						erosivity_path_cv = path	
				
	isdir = os.path.isdir(out_path)
	if(not isdir):
		os.mkdir(out_path)

	isdir = os.path.isdir(in_path)
	if(not isdir):
		os.mkdir(in_path)

	default_year = "YEAR_0"
	year_dir = "/YEAR_{}/".format(year)
		
	for parameter in parametersList:
		name = parameter[0]
		value = parameter[1]
		if (default_year in value):
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
		
		if (name == PRECIPITATION_DIR and precipitation_path_cv != ''):			
			if (model == 'swy'):
				region = getRegionFromId(basin)
				region_name = region[4]
				value = os.path.dirname(precipitation_path_cv) + "/" + region_name
				print ("get DIR for %s: %s" % (name, value))

		if (name == ET0_DIR and eto_path_cv != ''):
			if (model == 'swy'):
				region = getRegionFromId(basin)
				region_name = region[4]
				value = os.path.dirname(eto_path_cv) + "/" + region_name
				print ("get DIR for %s: %s" % (name, value))
			
		if(suffix):
			region = getRegionFromId(basin)
			value = region[4]
			
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
			default = 'y'
			#values, headers = getBiophysicParams(user, label, default)

			values,headers=getDefaultBiophysicParams(label,default)
			valuesUser,headersUser=getUserBiophysicParams(id_catchment,id_case,user,label,'N')
            # Reemplazar los parametros del usuario 
            # en los parametros por defecto
			for userIdx,valUser in enumerate(valuesUser):
				for defIdx,defVal in enumerate(values):
					if (valUser[0]==defVal[0]):
						values[defIdx]=valUser
			generateCsv(headers, values, file)
			value = file
		dictParameters[name] = value
	return dictParameters,out_path,label

def executeFunction(basin,model,type,catchments,id_usuario, year, id_case):
	logger.info("execFunction :: start")
	print(":: execFunction :: start")
	date = datetime.date.today()
	path = createFolder(id_usuario, id_case, date)

	list = getParameters(basin,model)	
	shp_catchment_path = exportToShp(catchments, path)
	id_catchment = catchments[0]
	parameters,pathF,label = processParameters(list,basin,shp_catchment_path,path,type,model,id_usuario, year, id_case, id_catchment)
	json_parameters = json.dumps(parameters, indent=2)
	print("writing file %s/parameters_.json" % (path))
	txt_file = open(os.path.join(path,"parameters_" + model + "_" + type + ".json"), "w")
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

	return shp_catchment_path,path,label


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

def timeImplementFromStudyCase(id):
	print("timeImplementFromStudyCase - id::%s" % id)
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	sql = "select time_implement from public.waterproof_study_cases_studycases where id = %s" % id
	cursor.execute(sql)
	year = 1
	try:
		row = cursor.fetchone()
		year = row[0]
	except:
		year=-1
	return year


# Insert Invest Result
def insertInvestResult(year, type, awy, wn_kg, wp_kg, wsed_ton, bf_m3, wc_ton,intake_id, study_case_id, user_id):
	listResult = []
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	cursor.callproc('__wp_invest_result_insert',[year, type, awy, wn_kg, wp_kg, wsed_ton, bf_m3, wc_ton,intake_id, study_case_id, user_id])
	conn.commit()
	cursor.close()
	conn.close()

''' Calculate Cost function '''
def costFunctionExecute(intake_id, study_case_id, user_id):

	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	cursor.callproc('__wp_get_function_cost_study_cases',[study_case_id])
	rows = cursor.fetchall()
	cursor.close()
	Q = 'Q'
	CN = 'CN'
	CP = 'CP'
	CSed = 'CSed'
	WN = 'WN'
	WP = 'WP' 
	WSed = 'WSed'
	WSedRet = 'WSedRet'
	WNRet = 'WNRet'
	WPRet = 'WPRet'
	expression = ''
	
	for row in rows:
		vars = dict()
		graphid = str(row[17])
		year = row[0]
		element = row[1]
		money = row[2]
		factor = float(row[3])
		stage = row[4]		
		awy = row[5]
		
		vars[Q + graphid] = row[6] 
		vars[CN + graphid] = row[7]
		vars[CP + graphid] = row[8]
		vars[CSed + graphid] = row[9]
		vars[WN + graphid] = row[10]
		vars[WP + graphid] = row[11]
		vars[WSed + graphid] = row[12]
		vars[WNRet + graphid] = row[13]
		vars[WPRet + graphid] = row[14]
		vars[WSedRet + graphid] = row[15]
		expression = row[16]
				
		if (not expression is None and expression.strip() != ''):
			args = re.findall(r'[a-zA-Z_]\w*', expression)
			ALLOWED_NAMES = {
				k: v for k, v in math.__dict__.items() if not k.startswith("__")
			}
			args = remove_no_vars(args)
			# global_vars = dict()
			# for v in args:
			# 	global_vars[v] = 1
			result = -99999
			try:
				code = compile(expression, "<string>", "eval")
				result = eval(code,vars,ALLOWED_NAMES)	
				result_factor = result * factor
			except:
				result = -99999

			cursor = conn.cursor()
			cursor.callproc('__wp_get_aggregate_result_function_cost',[stage, intake_id, element, year, result_factor, money, study_case_id, user_id])
			conn.commit()
			cursor.close()
	
	conn.close()
	return True

""" Remove special functions o math expressions"""
""" (i.e: min: E2, E3) """
def remove_no_vars(vars):

	special_values = ['min', 'E2', 'E3']
	# if (settings.WATERPROOF_SPECIAL_VALUES):
	#	special_values = settings.WATERPROOF_SPECIAL_VALUES
	for v in special_values:
		while v in vars:
			vars.remove(v)    
	return vars