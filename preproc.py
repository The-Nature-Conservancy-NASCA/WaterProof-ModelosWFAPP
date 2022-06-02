# Date: 24/09/2020
# Author: Diego Rodriguez - Skaphe Tecnologia SAS
# WFApp


# Importacion de librerias
from constants import INVEST_TYPE_CURRENT, INVEST_TYPE_NBS, INVEST_TYPE_QUALITY
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
import calculateConcentrations
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
import constants
from decimal import *
from rasterstats import zonal_stats
from dbfread import DBF
import pandas as pd
import numpy as np
import pysal as ps

logger = logging.getLogger(__name__) # grabs underlying WSGI logger
logger.setLevel(logging.INFO)

base_path = environ["PATH_FILES"]

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

# Exportar cuenca delimitada a shp
def exportToShp(catchment, path):
	print ("Exporting to shp...")
	params = config(section='postgresql_alfa')
	# connString = "PG: host=" + params['host'] + " dbname=" + params['database'] + " user=" + params['user'] + " password=" + params['password'] 
	# conn = ogr.Open(connString)
	# if conn is None:
	# 	print('Could not open a database or GDAL is not correctly installed!')
	# 	sys.exit(1)

	conn_ = connect('postgresql_alfa')
	cursor_ = conn_.cursor()

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
		sql = 'select id, "geomIntake" from waterproof_intake_polygon where intake_id %s' % params
		#layer = conn.ExecuteSQL(sql)
		cursor_.execute(sql)
		try:
			row = cursor_.fetchone()
			feat_coll = row[1] # data as json
			id = row[0]
			geom_intake = json.loads(feat_coll)['features'][0]['geometry']
			geom = ogr.CreateGeometryFromJson(json.dumps(geom_intake))
			#while feat is not None:
			featDef = ogr.Feature(out_layer.GetLayerDefn())
			#geom = feat.GetGeometryRef()
			geom.Transform(transform)		
			featDef.SetGeometry(geom)			
			featDef.SetField('ws_id',id)		
			featDef.SetField('subws_id',id)		
			out_layer.CreateFeature(featDef)
			#feat.Destroy()
			#	feat = layer.GetNextFeature()
		except:
			print ("No data found")
		
		#conn.Destroy()
		out_ds.Destroy()
		
	return os.path.join(os.getcwd(),output)

# Crear directorio para almacenar procesamientos
def createFolder(user, id_case, id_catchment ,date):
	usr_folder = "%s_%s_%s-%s-%s" % (user,id_case, date.year, date.month, date.day)
	out_folder = path.join(base_path,"salidas", usr_folder)
	wi_folder = "WI_%s" % (id_catchment)
	ptap_ids = ptap_ids_from_study_case(id_case)
	folders = {
		"in":[
			"catchment",
			"01-INVEST_QUALITY",
			"02-PREPROC_RIOS",
			"03-INVEST",
			"04-RIOS",
			"05-ROI",
			"06-AQUEDUCT",
			"07-DISAGGREGATION",
			"08-WATER_BALANCE",
		],
		"out":[
			"01-INVEST_QUALITY",
			"02-PREPROC_RIOS",
			"03-INVEST",
			"04-RIOS",
			"05-ROI",
			"06-AQUEDUCT",
			"07-DISAGGREGATION",
			"08-WATER_BALANCE",
		]
	}

	IN = 'in'
	OUT = 'out'
	ROI = 'ROI'
	isdir = path.isdir(out_folder)
	if(not isdir):
		os.mkdir(out_folder)

	out_folder_wi = path.join(out_folder, wi_folder)
	isdir = path.isdir(out_folder_wi)
	if(not isdir):
		os.mkdir(out_folder_wi)
		
	indicators_folder='INDICATORS'
	out_folder_indicators = path.join(out_folder, indicators_folder)
	isdir = path.isdir(out_folder_indicators)
	if(not isdir):
		os.mkdir(out_folder_indicators)
	
	# create directories for ptaps
	for ptap in ptap_ids:
		ptap_folder = "PTAP_%s" % (ptap)
		out_folder_ptap = path.join(out_folder, ptap_folder)
		isdir = path.isdir(out_folder_ptap)
		if(not isdir):
			os.mkdir(out_folder_ptap)
			os.mkdir(path.join(out_folder_ptap, IN))
			os.mkdir(path.join(out_folder_ptap, OUT))
			os.mkdir(path.join(out_folder_ptap, IN, '08-WATER_BALANCE'))
			os.mkdir(path.join(out_folder_ptap, OUT, '08-WATER_BALANCE'))

	# create directory for ROI
	out_folder_roi = path.join(out_folder, ROI)
	if(not path.isdir(out_folder_roi)):
		os.mkdir(out_folder_roi)
		os.mkdir(path.join(out_folder_roi, IN))
		os.mkdir(path.join(out_folder_roi, OUT))

	for key in folders:
		pathNew = os.path.join(out_folder_wi,key)
		isdirF = path.isdir(pathNew)
		if(not isdirF):
			os.mkdir(pathNew)
		for item in folders[key]:
			pathNew2 = os.path.join(out_folder_wi,key,item)
			isdirFF = path.isdir(pathNew2)
			if(not isdirFF):
				os.mkdir(pathNew2)
	
	return out_folder_wi
   
# Cortar raster
def cutRaster(catchment,path,out_path):
	print ("Cutting raster...")
	print ("Catchment: %s" % (catchment))
	print ("Path: %s" % (path))
	print ("Out path: %s" % (out_path))
	#data = rasterio.open(path)
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
	
	print ("os.path.basename(path): %s" % os.path.basename(path))
	print ("return : %s" % os.path.join(out_path,os.path.basename(path)))
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
		s,n,p,q,sW,nW,pW,bf = calculateConcentrations.calcConcentrations(pathWs,label,cont, sub_dir, year_dir)
	else:
		s,n,p,q,sW,nW,pW,bf = [-1,-1,-1,-1,-1,-1,-1,-1]
	
	if math.isnan(s):
		s = 0
	elif math.isnan(n):
		n = 0
	elif math.isnan(p):
		p = 0
	elif math.isnan(q):
		q = 0
	elif math.isnan(sW):
		sW = 0
	elif math.isnan(nW):
		nW = 0
	elif math.isnan(pW):
		pW = 0
	
	return s,n,p,q,sW,nW,pW,bf
 
#Calcular sumatoria de resultado de carbon
def calculateCarbonSum(catchment,path,label, model_dir, year_dir):
	stats = ['sum']
	#model_dir = '01-INVEST_QUALITY'
	raster = os.path.join(path,'out',model_dir,'CARBON', year_dir,'tot_c_cur_' + label + '.tif')
	statCalc = calculateStatistic(stats,raster,catchment)
	return statCalc

def getPathsClimateValueFromStudyCaseId(id_study_case, basin):
	print ("getPathsClimateValueFromStudyCaseId :: id_study_case : %s, basin: %s " % (id_study_case, basin))
	listResult = []
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	cursor.callproc('__wpget_paths_climate_value',[id_study_case, basin])
	result = cursor.fetchall()
	for row in result:
		print (row)
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
	# print("processParameters :: out_folder_quality :: {%s}" % {out_folder_quality})	
	
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

	if(type == INVEST_TYPE_QUALITY):
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

		if (type != INVEST_TYPE_CURRENT):
			paths_climate_value = getPathsClimateValueFromStudyCaseId(id_case, id_catchment)

			if (len(paths_climate_value) > 0):
				for p in paths_climate_value:
					path = p[2]
					if (PRECIPITATION in path):
						# print("Using Climate Value PATH for: %s" % PRECIPITATION)
						precipitation_path_cv = path
					elif (EVAPOTRANSPIRATION in path):
						eto_path_cv = path
						# print("Using Climate Value PATH for: %s" % EVAPOTRANSPIRATION)
					elif (RAINFALL_EROSIVITY in path):
						# print("Using Climate Value PATH for: %s" % RAINFALL_EROSIVITY)
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
		
		if ((name == 'lulc_path' or name == 'lulc_raster_path') and type == constants.INVEST_TYPE_NBS):
			path_coverages = 'out/04-RIOS/1_investment_portfolio_adviser_workspace/activity_portfolios/continuous_activity_portfolios/translated_cob/'
			raster_coverage_name = 'activity_portfolio_continuous_year_%s_FUTURE_COMPLETE.tif' % year
			value = os.path.join(pathF, path_coverages,raster_coverage_name)
					
		if (name == 'lulc_cur_path' and type == constants.INVEST_TYPE_NBS):
			path_coverages = 'out/04-RIOS/1_investment_portfolio_adviser_workspace/activity_portfolios/continuous_activity_portfolios/'
			raster_coverage_name = 'activity_portfolio_continuous_year_%s_FUTURE_COMPLETE.tif' % year
			value = os.path.join(pathF, path_coverages,"CARBON",raster_coverage_name)
				
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
	# print(":: execFunction :: start")
	date = datetime.date.today()
	id_catchment = catchments[0]
	path = createFolder(id_usuario, id_case, id_catchment ,date)

	list = getParameters(basin,model)	
	shp_catchment_path = exportToShp(catchments, path)
	
	parameters,pathF,label = processParameters(list,basin,shp_catchment_path,path,type,model,id_usuario, year, id_case, id_catchment)
	json_parameters = json.dumps(parameters, indent=2)
	param_path_file =  os.path.join(path,"parameters_" + model + "_" + type + "_" + str(year) + ".json")
	print(":: executeFunction :: writing file ::  %s " % (param_path_file))
	txt_file = open(param_path_file, "w")
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

def ptap_ids_from_study_case(studycase_id):
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	sql = "select header_id from public.waterproof_study_cases_studycases_ptaps where studycases_id = %s" % studycase_id
	cursor.execute(sql)
	result = cursor.fetchall()	
	cursor.close()
	return result


# Insert Invest Result
def insertInvestResult(year, type, awy, wn_kg, wp_kg, wsed_ton, bf_m3, wc_ton,intake_id, study_case_id, user_id):
	listResult = []
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	
	cursor.callproc('__wp_invest_result_insert',[year, type, validateNumber(awy), validateNumber(wn_kg), validateNumber(wp_kg), validateNumber(wsed_ton), validateNumber(bf_m3), validateNumber(wc_ton), intake_id, study_case_id, user_id])
	conn.commit()
	cursor.close()
	conn.close()

def costFunctionExecute(intake_id, study_case_id, user_id):
	print ("costFunctionExecute")
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	print ("study_case_id: %s" % study_case_id)
	stage = 'BAU'
	type_element = 'intake'
	
	print (stage, type_element)
	cursor = conn.cursor()
	cursor.callproc('__wp_get_function_cost_study_cases',[study_case_id, stage, type_element])
	rows = cursor.fetchall()
	cursor.close()
	internalCostFunctionExecute(conn, rows, study_case_id, user_id)

	stage = 'NBS'
	type_element = 'intake'
	print (stage, type_element)
	cursor = conn.cursor()
	cursor.callproc('__wp_get_function_cost_study_cases',[study_case_id, stage, type_element])
	rows = cursor.fetchall()
	cursor.close()
	internalCostFunctionExecute(conn, rows, study_case_id, user_id)

	stage = 'BAU'
	type_element = 'PTAP'
	print (stage, type_element)
	cursor = conn.cursor()
	cursor.callproc('__wp_get_function_cost_study_cases',[study_case_id, stage, type_element])
	rows = cursor.fetchall()
	cursor.close()
	internalCostFunctionExecute(conn, rows, study_case_id, user_id)

	stage = 'NBS'
	type_element = 'PTAP'
	print (stage, type_element)
	cursor = conn.cursor()
	cursor.callproc('__wp_get_function_cost_study_cases',[study_case_id, stage, type_element])
	rows = cursor.fetchall()
	cursor.close()
	internalCostFunctionExecute(conn, rows, study_case_id, user_id)

	# CUSTOM
	stage = 'NBS'
	type_element = 'intake'
	print (stage, type_element)
	cursor = conn.cursor()
	cursor.callproc('__wp_get_function_cost_study_cases_custom',[study_case_id, stage])
	rows = cursor.fetchall()
	cursor.close()
	internalCostFunctionExecute(conn, rows, study_case_id, user_id)

	stage = 'BAU'
	type_element = 'intake'
	print (stage, type_element)
	cursor = conn.cursor()
	cursor.callproc('__wp_get_function_cost_study_cases_custom',[study_case_id, stage])
	rows = cursor.fetchall()
	cursor.close()
	internalCostFunctionExecute(conn, rows, study_case_id, user_id)

	conn.close()
	
	return True


def internalCostFunctionExecute(conn, rows, study_case_id, user_id):
	print("internalCostFunctionExecute")
	
	years = []
	intakes = []
	# save years
	for row in rows:
		if not row[0] in years:
			years.append(row[0])

	# save intakes
	for row in rows:
		if not row[20] in intakes:
			intakes.append(row[20])

	for intake in intakes:
		for y in years:	
			print ("Iterating Year : %s" % y)
			vars = dict()
			for row in rows:
				year = row[0]
				intake_ptap_id = row[20]
				if y == year and intake == intake_ptap_id:
					graphid = str(row[17])
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
			
			for row in rows:			
				if (len(row) > 19):
					year = row[0]
					intake_ptap_id = row[20]
					if y == year and intake == intake_ptap_id:
						type_desc = str(row[18])
						function_id = row[19]
						intake_ptap_id = row[20]			
						element = row[1]
						money = row[2]
						factor = row[3]
						stage = row[4]		
						awy = row[5]
						ratio_change = row[21]

						expression = row[16]
						if (factor is None):
							factor = 1.0

						if (ratio_change is None):
							ratio_change = 1.0

						print ("stage: %s :: type: %s :: element: %s :: factor : %s" % (stage, type_desc, element, factor))	
						if (not expression is None):
							if expression.strip() != '':
								print ("expression: %s" % expression )
								args = re.findall(r'[a-zA-Z_]\w*', expression)
								ALLOWED_NAMES = {
									k: v for k, v in math.__dict__.items() if not k.startswith("__")
								}
								args = remove_no_vars(args)
								
								# result = -99999.0
								result_factor = 1.0
								try:						
									code = compile(expression, "<string>", "eval")								
									result = eval(code,vars,ALLOWED_NAMES)
									print ("result from eval:")	
									print (result)
									result_factor = (result * factor)/ratio_change
									print ("result factor= (result*factor)/ratio_change :  (%s*%s)/%s = %s" % (result, factor, ratio_change, result_factor))								
								except:
									print ("ERROR!!!")
									result = -99999

								try:
									cursor = conn.cursor()
									cursor.callproc('__wp_get_aggregate_result_function_cost',[stage, intake_ptap_id, element, year, result_factor, money, study_case_id, user_id, type_desc, function_id])
									conn.commit()
									cursor.close()							
								except:
									print("Error saving data using __wp_get_aggregate_result_function_cost ")
							
	return True

""" Remove special functions o math expressions"""
""" (i.e: min: E2, E3) """
def remove_no_vars(vars):	

	special_values = ['min', 'E2', 'E3', 'if', 'else', 'E']
	# if (settings.WATERPROOF_SPECIAL_VALUES):
	#	special_values = settings.WATERPROOF_SPECIAL_VALUES
	for v in special_values:
		while v in vars:
			vars.remove(v)    
	return vars


def bio_params_by_condition(region, study_case_id):
	print("bio_params_by_condition")
	
	# path_future_lulc = pathLULC.replace(constants.RIOS_DIR,constants.PREPROC_RIOS_DIR).replace('.tif','_FUTURE.tif')
	
	conn = connect('postgresql_alfa')
	cursor = conn.cursor()
	cursor.callproc('__wp_get_biophysycal_by_condition',[study_case_id, region])
	result = cursor.fetchall()
	# fields : lucode, usle_c, usle_p
	conn.commit()
	cursor.close()	
	values = []
	for t in result:
		values.append(t[0])
	print ("values :%s " % values)	
	return values 

def rasters_statistics(usr_folder, intake_id,year, region):

	init_path = '/home/skaphe/Documentos/tnc/modelos/salidas'
	base_path = init_path + '/%s/WI_%s/out/03-INVEST' % (usr_folder, intake_id)
	catchment = init_path + '/%s/WI_%s/in/catchment/catchment.shp' % (usr_folder, intake_id)
	awy   = base_path + '/AWY/YEAR_%s/output/per_pixel/wyield_%s.tif' % (year, region)
	sdr   = base_path + '/SDR/YEAR_%s/sed_export_%s.tif' % (year, region)
	swy   = base_path + '/SWY/YEAR_%s/B_%s.tif' % (year, region)
	ndr_n = base_path + '/NDR/YEAR_%s/n_export_%s.tif' % (year, region)
	ndr_p = base_path + '/NDR/YEAR_%s/p_export_%s.tif' % (year, region)
	carbon = base_path + '/CARBON/YEAR_%s/tot_c_cur_%s.tif' % (year, region)

	types_stats = "min mean max"
	raster_list = dict()
	raster_list['awy'] = zonal_stats(catchment,awy,stats=types_stats,all_touched=True)
	raster_list['sdr'] = zonal_stats(catchment,sdr,stats=types_stats,all_touched=True)
	raster_list['swy'] = zonal_stats(catchment,swy,stats=types_stats,all_touched=True)
	raster_list['ndr_n'] = zonal_stats(catchment,ndr_n,stats=types_stats,all_touched=True)
	raster_list['ndr_p'] = zonal_stats(catchment,ndr_p,stats=types_stats,all_touched=True)
	raster_list['carbon'] = zonal_stats(catchment,carbon,stats=types_stats,all_touched=True)

	return raster_list

def SDR_BugFix(FilePath_BaU, FilePath_NBS, Region):
    """
    FilePath_BaU: SDR model output directory for BaU scenario
    FilePath_NBS: SDR model output directory for NBS scenario
    Region: Analysis region suffix
    """

    # Open SDR - BaU
    SDR_BaU_Tif = rasterio.open(os.path.join(FilePath_BaU,'sed_export_' + Region + '.tif'))
    SDR_BaU     = SDR_BaU_Tif.read(1)
    SDR_BaU_Tif.close()

    # Open SDR - NBS
    SDR_NBS_Tif = rasterio.open(os.path.join(FilePath_NBS,'sed_export_' + Region + '.tif'))
    NoValue     = SDR_NBS_Tif.nodata
    SDR_NBS     = SDR_NBS_Tif.read(1)
    Param       = {'height': SDR_NBS_Tif.shape[0],
                   'width': SDR_NBS_Tif.shape[1],
                   'crs': SDR_NBS_Tif.crs,
                   'transform': SDR_NBS_Tif.transform}
    SDR_NBS_Tif.close()

    # Correct
    Posi = SDR_BaU < SDR_NBS
    SDR_NBS[Posi] = SDR_BaU[Posi]

    # Save Results
    with rasterio.open(
        os.path.join(FilePath_NBS,'sed_export_' + Region + '.tif'),'w',
        driver='GTiff',
        height= Param['height'],
        width=Param['width'],
        count=1,
        dtype=SDR_NBS.dtype,
        crs=Param['crs'],
        transform=Param['transform'],
        nodata=NoValue
    ) as dst:
        dst.write(SDR_NBS, 1)

    # ------------------------------------------------------------------------------------------------------------------
    # Zonal Statistics
    # ------------------------------------------------------------------------------------------------------------------
    New_Export = np.sum(SDR_NBS[SDR_NBS != NoValue])

    # ------------------------------------------------------------------------------------------------------------------
    # Change DBF
    # ------------------------------------------------------------------------------------------------------------------
    # Open DBF
    FileName_DBF    = 'watershed_results_sdr_' + Region + '.dbf'
    Table_DBF       = DBF(os.path.join(FilePath_NBS,FileName_DBF))
    Table_PD        = pd.DataFrame(iter(Table_DBF))

    # Change sed_export Data - DBF
    Table_PD['sed_export'] = New_Export

    # adaptation of the function `df2dbf` to write your resulting dbf file
    type2spec = {int: ('N', 20, 0),
                 np.int64: ('N', 20, 0),
                 float: ('N', 36, 15),
                 np.float64: ('N', 36, 15),
                 np.float32: ('N', 36, 15),
                 str: ('C', 14, 0)}

    types = [type(Table_PD[i].iloc[0]) for i in Table_PD.columns]
    specs = [type2spec[t] for t in types]

    # Save Dbf
    db = ps.open(os.path.join(FilePath_NBS,FileName_DBF), 'w')
    db.header = list(Table_PD.columns)
    db.field_spec = specs
    for i, row in Table_PD.T.iteritems():
        db.write(row)
    db.close()

# validate if number is null , return zero otherwise return the number
def validateNumber(value):
	print ("validateNumber. value : %s " % value)
	if value == None or math.isnan(value):
		return 0
	else:
		return value