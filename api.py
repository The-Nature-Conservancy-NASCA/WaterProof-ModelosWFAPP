import shutil
from celery.result import AsyncResult
from fastapi import Body, FastAPI, Form, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import List
import delineate
from pathlib import Path
import os
from os import environ,path, rmdir
import preproc
import datetime
from aqueduct import cutAqueduct,insertResults
from ptapSelection import getRandomLetter as grl
from getDataInWB import DataInWB, DataInWBPTAP, DataInBAU, DataInNBS, DataInBAUPTAP, DataInNBSPTAP
from WI_Balance import execWB
from outWB import mergeData, readSum, mergeDataPTAP, readSumPTAP
from outWBDisIntake import SaveInDB
from pydantic import BaseModel
from getDataPTAP import generateAll
from Select_PTAP import Select_PTAP
from reclassify import reclassifyFilesInFolder,verifypathconti
from dissagregation import DataCSVDis,DisaggregationOut
from ROIFunctions.roiOut import SaveRoiDB, CreateZip
from ROIFunctions.roiIn import DataCSVRoi
from ROIFunctions.exchangeRateROI import ExchangeROI
from ROIFunctions.common_functions import path_wb,updateDataDB,CopyFile,insertParameter,selectDataDB
from IndicatorsFunctions.Indicators_IN_and_OUT import IndicatorsIn,IndicatorsSaveDB
import pandas as pd
import requests
from Disaggregation_WaterFunds.Disaggregation_and_Convolution import Desaggregation_BaU_NBS
from ROI_WaterFunds.ROI import ROI_Analisys
from Indicators_WaterFunds.Indicators_WaterFunds import Indicators_BaU_NBS
import logging
import ptvsd
import constants
from pprint import pformat
import aiohttp
import asyncio
import aiofiles
from aiohttp import ClientSession
from worker import create_task, catchment_task, exec_invest_task

base_path = environ["PATH_FILES"]
logger = logging.getLogger(__name__) # grabs underlying WSGI logger
logger.setLevel(logging.DEBUG)
today = datetime.date.today()
datefilelog = today.strftime("%d-%b-%Y_%I_%M")
loginfodate = today.strftime("%d/%b/%Y %I:%M:%S %p")

# Only attach the debugger when we're the Django that deals with requests
# if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
ptvsd.enable_attach(address=('0.0.0.0', 3000), redirect_output=True)


# from workers import execInv

class ListCS(BaseModel):
    csinfras: List[int]

app = FastAPI()

origins = [
    "http://apps.skaphe.com:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def fetch_html(url: str, session: ClientSession, **kwargs) -> str:
	"""GET request wrapper to fetch page HTML.
	kwargs are passed to `session.request()`. """

	resp = await session.request(method="GET", url=url, **kwargs)
	resp.raise_for_status()
	logger.info("Got response [%s] for URL: %s", resp.status, url)
	html = await resp.text()
	return html

async def execute_preproc(session, url, params):
	"""execute_preproc (asynchronously)"""
	logger.info("Executing preproc :: async")
	print("Executing preproc :: async")
	try:
		response = await session.request(method='GET', url=url, params=params)
		response.raise_for_status()
		print(f"Response status ({url}): {response.status}")    
	except Exception as err:
		print(f"An error ocurred: {err}")
	response_json = await response.json()
	return response_json

@app.get("/wf-models/")
async def root():
	logger.debug("Hello world")
	print("Hello world  with print")
	return {"message":"Hello World :: %s" % {__name__}}

@app.get("/wf-models/test_shp")
async def test_shp(id:int):
	logger.info(f'Start Process test_shp {id}')
	print(f'Start Process test_shp {id}')
	path = '/home/skaphe/Documentos/tnc/modelos/salidas/tmp/'
	preproc.exportToShp([str(id)], path)


@app.get("/wf-models/rios")
async def test_rios():
	logger.debug("testing rios frop wf-models")
	print("testing rios frop wf-models")
	base_url_api = 'http://wfapp_py2:5050/wf-rios/welcome/'
	r = requests.get(url=base_url_api)
	data = r.json()
	return data


@app.get("/wf-models/preprocRIOS")
async def preproc_rios(id_usuario:str, id_case:int):
	logger.info('Start preprocRIOS from Models Py3 with async-await')
	print('Start preprocRIOS from Models Py3')
	base_url_api = 'http://wfapp_py2:5050/wf-rios/preprocRIOS/'
	parameters = {
		'id_usuario': id_usuario,
		'id_case' : id_case
  }
	async with ClientSession() as session:
		await asyncio.gather(*[execute_preproc(session, base_url_api, parameters)])

'''0. Exchange rate'''
@app.get("/wf-models/exchangeRate")
def exchangeRoi(study_case_id):
	logger.info('Start Proccess Exchange Rate')
	try:
		id = int(study_case_id)
		ExchangeROI(id)
	except Exception as e:
		logger.error('Error in Process Exchange Rate: ')
		logger.error(e.args)
		return e.args

	logger.info('Successfull Execution Process Exchange Rate')
	return "Run successful"

@app.get("/wf-models/cobTrans")
async def coverageTranslator(pathCobs, pathLULC, basin, study_case_id, catchmentOut):	
	folder = Path(pathCobs).parents[4]
	filenamelog = path.join(folder,f'log_{study_case_id}_{datefilelog}.log')
	formatlog = '%(asctime)s - %(levelname)s - %(message)s'
	logging.basicConfig(filename=filenamelog, format=formatlog, force=True, datefmt='%m/%d/%Y %I:%M:%S %p')
	logger.info('Start process Coverage translator')
	
	print ("cobTrans :: start")
	dictResult = dict()
	dictResult['status'] = True
	try:
		id = int(study_case_id)
		year = preproc.analysisPeriodFromStudyCase(id)
		region = preproc.getRegionFromId(basin)
		region_name = region[4]
		print ("year: %s :: region: %s" % (year, region_name))
		args = [id,filenamelog]
	
		# se adiciona este bloque para garantizar que exista el registro de generación del archivo zip
		count = selectDataDB('select count(*) from waterproof_reports_zip where study_case_id_id = %s' % id)
		if( count[0] == 0 ):
			insertParameter('__wpinsert_download_zip',args)
		pathCobs, json = verifypathconti(pathCobs)
		paths = reclassifyFilesInFolder(pathCobs,pathLULC, False,'', year, region_name,json, id, catchmentOut)
		path_future_lulc = pathLULC.replace(constants.RIOS_DIR,constants.PREPROC_RIOS_DIR).replace('.tif','_FUTURE.tif')
		if (os.path.isfile(path_future_lulc)):
			paths_future = reclassifyFilesInFolder(pathCobs,pathLULC, True, path_future_lulc, year, region_name, json, id, catchmentOut)
		dictResult['result'] = {"result":'successful execution'}
		dictResult['paths'] = paths
		dictResult['paths_future'] = paths_future
		logger.info('Successful execution process Coverage translator')
	except Exception as e:
		logger.error("Error in process Coverage translator")
		logger.error(e.args)
		dictResult['status'] = False
		dictResult['error'] = e.args

	logger.info(pformat(dictResult))
	return dictResult

'''4. Invest Excecution'''
@app.get("/wf-models/execInvest")
async def execInvest(type:str,id_usuario:int, basin:int, case:int, models: List[str] = Query(None),catchment:List[int] = Query(None)):
	logger.info('Start Process ExecInvest, Type: %s' % type)
	print("execInvest start, Type: %s" % type)
	dictResult = dict()
	dictResult['status'] = False
	catch = sorted(catchment,key=int)
	year = "0"

	type = type.upper()

	if type == constants.INVEST_TYPE_NBS:
		year = preproc.timeImplementFromStudyCase(case)
	if type == constants.INVEST_TYPE_BAU:
		year = preproc.analysisPeriodFromStudyCase(case)
	elif type == constants.INVEST_TYPE_CURRENT:
		year = 0
	carbon = False
	try:
	
		model_dir = constants.INVEST_QUALITY_DIR
		year_dir = 'YEAR_' + str(year)
		if(type != constants.INVEST_TYPE_QUALITY):
			model_dir = '03-INVEST';

		for model in models:
			#logger.debug("executeFunction for model :: %s" % {model})
			logger.info("Execute Function for model :: %s" % {model})
			#print(":: executeFunction for model :: %s" % {model})
			if type == constants.INVEST_TYPE_NBS:
				for y in range(1,year+1):
					logger.info(":: executeFunction model %s , Type: NBS for Year :: %s of %s" % (model, y, year))
					print(":: executeFunction model %s , Type: NBS for Year :: %s of %s" % (model, y, year))
					catchmentShp,path,label = preproc.executeFunction(basin,model,type,catchment,id_usuario, y, case)
			else:
				catchmentShp,path,label = preproc.executeFunction(basin,model,type,catchment,id_usuario, year, case)
			if (model == 'carbon'):
				carbon = True
	
		dictResult['result'] = 'successful execution for type :: {}'.format(type)
		dictResult['result'] = {}
		sum_carbon = -999 # TODO :: Validate if can be negative as disable value
		sum_carbon_val = -999
		sum_carbon_nbs = dict()
		if (carbon):
			logger.info("Calculate carbon sum")
			print ("Calculate carbon sum")
			if type == constants.INVEST_TYPE_NBS:
				for y in range(1,year+1):
					y_dir = 'YEAR_' + str(y)
					sum_carbon = preproc.calculateCarbonSum(catchmentShp,path,label, model_dir, y_dir)
					sum_carbon_val = sum_carbon[0]['sum']
					sum_carbon_nbs[y] = sum_carbon_val
			else:
				sum_carbon = preproc.calculateCarbonSum(catchmentShp,path,label, model_dir, year_dir)
				sum_carbon_val = sum_carbon[0]['sum']

		if(type == constants.INVEST_TYPE_QUALITY or type == constants.INVEST_TYPE_BAU or 
			type == constants.INVEST_TYPE_CURRENT or type == constants.INVEST_TYPE_NBS):
			if(type == constants.INVEST_TYPE_QUALITY ):
				updateDataDB( [catch[0]], "__wp_intake_emptycols" ) # sino es quality no entra

			execute = preproc.verifyExec(path, model_dir)
			cont = 0
			dictResult['result'] = []
			
			region 			= preproc.getRegionFromId(basin)
			region_name = region[4]
			year_bau 		= preproc.analysisPeriodFromStudyCase(case)
			base_path 	= path + '/out/03-INVEST'
			sdr_bau_path= base_path + '/SDR/YEAR_%s' % (year_bau)
			print ("sdr_bau : %s" % sdr_bau_path)
			print ("region: %s" % region_name)

			if type == constants.INVEST_TYPE_NBS:
				for y in range(1,year+1):					
					year_dir = 'YEAR_' + str(y)

					# FIXES
					# BAU == Last Year
					# NBS == from Year == 1 to Last Year					
					sdr_nbs_path	= base_path + '/SDR/YEAR_%s' % (y)
					print ("sdr_nbs_path :%s" % sdr_nbs_path)
					preproc.SDR_BugFix(sdr_bau_path, sdr_nbs_path, region_name)
					# FIXES

					for c in catch:
						s,n,p,q,sW,nW,pW,bf = preproc.calcConc(execute,path,label,cont, model_dir, year_dir)
						result = {
							"catchment": c,
							"carbon" : sum_carbon_nbs[y],	
							"awy": q,
							"year" : y,
							"w": {
								"sediment":sW,
								"nitrogen":nW,
								"phosporus":pW
							},
							"concentrations": {
								"sediment":s,
								"nitrogen":n,
								"phosporus":p
							}
						}	
						logger.info(f'Succesful {type} Execution')
						dictResult['result'].append(result)					
						preproc.insertInvestResult(y,type,q,nW,pW,sW,bf,sum_carbon_nbs[y],c, case, id_usuario)
			else:
				for c in catch:
					s,n,p,q,sW,nW,pW,bf = preproc.calcConc(execute,path,label,cont, model_dir, year_dir)
								
					preproc.InsertQualityParameters(c,'RIVER',q,sW,nW,pW,s,n,p)
					result={
						"catchment": c,
						"carbon" : sum_carbon,	
						"awy": q,
						"year" : year,
						"w": {
							"sediment":sW,
							"nitrogen":nW,
							"phosporus":pW
						},
						"concentrations": {
							"sediment":s,
							"nitrogen":n,
							"phosporus":p
						}
					}
					logger.info(f'Succesful {type} Execution')
					dictResult['result'].append(result)
					cont = cont + 1
					if (type != constants.INVEST_TYPE_QUALITY):
						preproc.insertInvestResult(year,type,q,nW,pW,sW,bf,sum_carbon_val,c, case, id_usuario)
				
		elif type == constants.INVEST_TYPE_CURRENT:
			# Nothing ToDo, is equal to quality
			dictResult['result']=[]
			print (type)
			for c in catch:
				result = {
						"catchment": c,
						"carbon" : sum_carbon,					
					}

				logger.info(f'Succesful {type} Execution')
				dictResult['result'].append(result)
			# dictResult['result'] = 'Ejecucion exitosa current scenario'

		# Revisar para solicitar como parámetro el ultimo año
		# TODO :: Revisar para implementar
		# elif type == "BaU":  
		#	dictResult['result'] = 'Ejecucion exitosa BaU'
		
		# TODO :: Revisar para implementar
		# Se ejecuta una vez x cada año
		# capa lulc tomada del resultado del traductor de cobertura	
		elif type == constants.INVEST_TYPE_NBS:  
			logger.info('Succesful NBS Execution')
			dictResult['result'] = 'Succesful NBS Execution'


		dictResult['status'] = True
		print(dictResult)

	except Exception as e:
		logger.error('Error in Process ExecInvest')
		logger.error(e.args)
		dictResult['status'] = False
		dictResult['error'] = e.args

	logger.info(dictResult)
	return dictResult

'''5. Disaggregation Execution'''
@app.get("/wf-models/disaggregation")
async def disaggregation( id_usuario, basin, case, catchment):
	logger.info('Start Proccess Disaggregation')
	try:
		print ("disaggregation")
		wi_folder = "WI_%s" % (catchment)
		date = datetime.date.today()
		usr_folder = "%s_%s_%s-%s-%s" % (id_usuario,case, date.year, date.month, date.day)
		# /home/skaphe/Documentos/tnc/salidas/1000_120_2021-05-10/WI_44/in/07-DISAGGREGATION
		path_data_in = path.join(base_path, constants.OUT_BASE_DIR, usr_folder, wi_folder, "in", constants.DISAGGREGATION_DIR)
		print("path_data_in : %s" % path_data_in)
		# /home/skaphe/Documentos/tnc/salidas/1000_120_2021-05-10/WI_44/out/07-DISAGGREGATION
		path_data_out = path.join(base_path, constants.OUT_BASE_DIR, usr_folder, wi_folder, "out", constants.DISAGGREGATION_DIR)
		print("path_data_out : %s" % path_data_out)
		dict_result = dict()
		dict_result['status'] = True
		DataCSVDis(path_data_in, catchment, case)
		Desaggregation_BaU_NBS(path_data_in, path_data_out)
		DisaggregationOut(path_data_out,catchment,case)
	except Exception as e:
		logger.info('Error in Proccess Disaggregation')
		logger.info(e.args)
		dict_result['status'] = False
		dict_result['error'] = e.args

	logger.info('Successfull Execution Process Disaggregation')
	return dict_result

# WB intake primera ejecucion tomando los valores de disaggregation
'''6. Water Balance Disaggregation Execution'''
@app.get("/wf-models/wbdisaggregationIntake")
async def calculateWBDisaggregationIntake(id_intake,user_id,study_case_id):
	function_db = "__wp_intake_insert_report"
	dictResult = dict()
	dictResult['status'] = False
	path_data_wb_in, path_data_wb_out, path_data_ds_out = path_wb(id_intake,user_id,study_case_id, 'WI')
	logger.info(f'Start Process Water Balance Disaggregation Intake {id_intake}')
	try:
		DataInBAU(id_intake,path_data_wb_in,path_data_ds_out,study_case_id)
		execWB(path_data_wb_in, path_data_wb_out)
		SaveInDB( function_db, id_intake, user_id, study_case_id, "BAU", path_data_wb_out,'Intake')
		DataInNBS(id_intake,path_data_wb_in,path_data_ds_out,study_case_id)
		execWB(path_data_wb_in, path_data_wb_out)
		SaveInDB( function_db, id_intake, user_id, study_case_id, "NBS", path_data_wb_out,'Intake')
		dictResult = dict()
		dictResult['status'] = True
		dictResult['result'] = {"result":'Transacción exitosa'}
	except Exception as e:
		logger.error(f'Error in Proccess Water Balance Disaggregation Intake {id_intake}')
		logger.error(e.args)
		dictResult['status'] = False
		dictResult['error'] = e.args

	logger.info(f'Successfull Execution in Proccess Water Balance Disaggregation Intake {id_intake}')
	return dictResult

'''7. Aqueduct Execution'''
@app.get("/wf-models/aqueduct")
async def calculateAqueduct(path,id_intake):
	# path = 1000_142_2021-6-25/WI_222
	# base_path =  /home/skaphe/Documentos/tnc/modelos/salidas
	full_path =  os.path.join(base_path, path)
	dictResult = dict()
	dictResult['status'] = False
	logger.info('Start Proccess Aqueduct')
	try:
		list = cutAqueduct(full_path)
		print(list)
		insertResults(list,id_intake)
		dictResult = dict()
		dictResult['status'] = True
		dictResult['result'] = list
	except Exception as e:
		logger.error('Error Execution in Proccess Aqueduct')
		logger.error(e.args)
		dictResult['status'] = False
		dictResult['error'] = e.args

	logger.info('Successfull Execution in Proccess Aqueduct')
	logger.info(dictResult)
	return dictResult

@app.post("/wf-models/ptapSelection")
async def ptapSelect(listcs:ListCS):
	dictResult = dict()
	dictResult['status'] = False
	# try:
	result = generateAll(listcs.csinfras)
	r,awy,cn,cp,cs,wn,wp,ws = Select_PTAP(result)
	dictResult = dict()
	dictResult['status'] = True
	dictResult['result'] = {
		"ptap_type":r,
		"awy":awy,
		"cn": cn,
		"cp": cp,
		"cs": cs,
		"wn": wn,
		"wp": wp,
		"ws": ws
		}
	# except Exception as e:
	# 	dictResult['status'] = False
	# 	dictResult['error'] = e.args
	return dictResult

# WB PTAP primera ejecucion tomando los valores de disaggregation
'''7. Water Balance Dissagregation PTAP Execution'''
@app.get("/wf-models/wbdisaggregationPTAP")
async def calculateWBDisaggregationPTAP(ptap_id,user_id,study_case_id):
	function_bd = '__wp_ptap_insert_report'
	dictResult = dict()
	dictResult['status'] = False

	path_data_wb_in, path_data_wb_out, path_data_ds_out = path_wb(ptap_id,user_id,study_case_id, 'PTAP')
	logger.info(f'Start Process Water Balance Disaggregation PTAP {ptap_id}')
	try:
		DataInBAUPTAP(ptap_id,study_case_id, path_data_wb_in, path_data_ds_out)
		execWB(path_data_wb_in, path_data_wb_out)
		SaveInDB( function_bd, ptap_id, user_id, study_case_id, 'BAU', path_data_wb_out,'PTAP')
		DataInNBSPTAP(ptap_id,study_case_id, path_data_wb_in)
		execWB(path_data_wb_in, path_data_wb_out)
		SaveInDB( function_bd, ptap_id, user_id, study_case_id, 'NBS', path_data_wb_out,'PTAP')
		dictResult = dict()
		dictResult['status'] = True
		dictResult['result'] = {"result":'Transacción exitosa'}
	except Exception as e:
		logger.error(f'Error in Proccess Water Balance Disaggregation PTAP {ptap_id}')
		logger.error(e.args)
		dictResult['status'] = False
		dictResult['error'] = e.args

	logger.info(f'Successfull Execution in Proccess Water Balance Disaggregation PTAP {ptap_id}')
	return dictResult

'''8. Execute Cost Function'''
@app.get("/wf-models/costFunctionExecute")
def costFunctionExecute(user_id, intake_id, study_case_id):
	
	preproc.costFunctionExecute(intake_id, study_case_id, user_id)
	return True

'''9. Indicators Execution'''
@app.get("/wf-models/indicators")
def indicators( user_id, study_case_id ):

	today = datetime.date.today()
	usr_folder = "%s_%s_%s-%s-%s" % (user_id, study_case_id, today.year, today.month, today.day)
	OUT_BASE_DIR = "salidas"
	INDICATORS = 'INDICATORS'
	path_data = path.join(base_path, OUT_BASE_DIR, usr_folder)
	path_data_ind = path.join(path_data,INDICATORS)
	dict_result = dict()
	dict_result['status'] = True
	logger.info('Start Proccess Indicators')
	try:
		IndicatorsIn(path_data)
		Indicators_BaU_NBS(path_data_ind)
		IndicatorsSaveDB(path_data,user_id,study_case_id,today)
	except Exception as e:
		logger.error('Error in Process Indicators')
		logger.error(e.args)
		dict_result['estado'] = False
		dict_result['error'] = e.args

	logger.info('Successfull Execution Process Indicators')
	return dict_result

'''10. ROI Execution'''
@app.get("/wf-models/roiExecution")
def roiExecution(user_id, study_cases_id):
	today = datetime.date.today()
	usr_folder = "%s_%s_%s-%s-%s" % (user_id, study_cases_id, today.year, today.month, today.day)
	OUT_BASE_DIR = "salidas"
	ROI = 'ROI'
	out_file = path.join(base_path, OUT_BASE_DIR,'README.txt')
	path_data = path.join(base_path, OUT_BASE_DIR, usr_folder)
	path_data_roi = path.join(path_data,ROI)
	dict_result = dict()
	dict_result['status'] = True
	logger.info('Start Proccess ROI Execution')
	try:
		DataCSVRoi(user_id, study_cases_id, today, path_data)
		ROI_Analisys(path_data_roi)
		SaveRoiDB(path_data_roi,study_cases_id)
		CopyFile(out_file,path.join(path_data,'README.txt'))
		CreateZip(path_data, study_cases_id, usr_folder)
	except Exception as e:
		logger.error('Error in Process ROI Execution')
		logger.error(e.args)
		dict_result['estado'] = False
		dict_result['error'] = e.args

	logger.info('Successfull Execution Process ROI Execution')
	return dict_result
	# return preproc.processRoi(user_id,study_cases_id)

# water balance segunda ejecucion Intake
@app.get("/wf-models/wb")
async def calculateWB(id_intake):
	logger.info(f'Start Process Water Balance {id_intake}')
	print(f'Start Process Water Balance {id_intake}')
	dictResult = dict()
	dictResult['status'] = False
	OUT_BASE_DIR = "salidas"
	path_data_wb_in = path.join(base_path, OUT_BASE_DIR, 'tmp')
	path_data_wb_out = path.join(base_path, OUT_BASE_DIR, 'tmp')
	logger.info(f'Start Process Water Balance Intake {id_intake}')
	try:
		print(f'Start method DataInWB {id_intake}')
		DataInWB(id_intake, path_data_wb_in)
		print(f'Start method execWB {id_intake}')
		execWB(path_data_wb_in, path_data_wb_out)
		print(f'Start method mergeData {id_intake}')
		outFile = mergeData(path_data_wb_out)
		print(f'Start method readSum {id_intake}')
		readSum(outFile, path_data_wb_out)
		dictResult = dict()
		dictResult['status'] = True
		dictResult['result'] = {"result":'Transacción exitosa'}
	except Exception as e:
		logger.error(f'Error in Proccess Water Balance Intake {id_intake}')
		logger.error(e.args)
		dictResult['status'] = False
		dictResult['error'] = e.args

	logger.info(f'Successfull Execution in Proccess Water Balance Intake {id_intake}')
	return dictResult

# water balance segunda ejecucion PTAP
@app.get("/wf-models/wbPTAP")
async def calculateWBPTAP(id_ptap):
	dictResult = dict()
	dictResult['status'] = False
	logger.info(f'Start Process Water Balance PTAP {id_ptap}')
	try:
		ptap_id = int(id_ptap)
		DataInWBPTAP(ptap_id)
		execWB()
		outFile = mergeDataPTAP()
		readSumPTAP(outFile)
		dictResult['status'] = True
		dictResult['result'] = {"result":'Transacción exitosa'}
	except Exception as e:
		logger.error(f'Error in Proccess Water Balance PTAP {id_ptap}')
		logger.error(e.args)
		dictResult['status'] = False
		dictResult['error'] = e.args

	logger.info(f'Successfull Execution Proccess Water Balance PTAP {id_ptap}')
	return dictResult

@app.get("/wf-models/disaggregation2")
def disaggregation2(user_id, study_cases_id):

	return preproc.processDissagregation(user_id, study_cases_id)

@app.get("/wf-models/download")
def download(user_dir, topic , file):
	PATH_FILES = os.environ["PATH_FILES"]
	path = os.path.join(PATH_FILES,'salidas', user_dir)
	file_path = os.path.join(path,'out' , topic, file)
	print ("download file : " + file_path)
	return FileResponse(path=file_path, filename=file, media_type='text/csv')

@app.get("/download")
def download(user_dir, topic , file):
	PATH_FILES = os.environ["PATH_FILES"]
	path = os.path.join(PATH_FILES,'salidas', user_dir)
	file_path = os.path.join(path,'out' , topic, file)
	print ("download file : " + file_path)
	return FileResponse(path=file_path, filename=file, media_type='text/csv')

def validate_and_create_dir(dir_to_validate):

	if(not os.path.isdir(dir_to_validate)):
		os.mkdir(dir_to_validate)

@app.get("/wf-models/delete")
def delete(study_case_id,user_id,date):
	try:
		pathdelete = os.path.join(base_path,'salidas',user_id+'_'+study_case_id+'_'+date)
		shutil.rmtree(pathdelete)
	except Exception as e:
		return e.args
	return 'file delete complete!'

@app.get("/wf-models/delete-intake")
def delete(intake_id,user_id,date):
	try:
		pathdelete = os.path.join(base_path,'salidas',user_id+'_'+'-1'+'_'+date+'/WI_'+intake_id)
		shutil.rmtree(pathdelete)
	except Exception as e:
		return e.args
	return 'file delete complete!'

@app.get("/wf-models/snapPoint")
async def snap(x,y):
	dictResult = dict()
	dictResult['status'] = False
	try:
		x = float(x)
		y = float(y)
		basin = delineate.getRegionFromCoord(x,y)
		dictResult['basin'] = basin
		path = delineate.getPath(basin,2)
		dictResult['path'] = path
		path = delineate.cutRaster(path,x,y,5)
		dictResult['path_raster'] = path
		[x,y] = delineate.snap(path,x,y)
		dictResult = dict()
		dictResult['status'] = True
		dictResult['result'] = {"x_snap":x,"y_snap":y}
	except Exception as e:
		dictResult['status'] = False
		dictResult['error'] = e.args
	return dictResult
 
@app.get("/wf-models/delineateCatchment")
async def delineateCatchment(x,y):
	logger.info(f'Start Process delineateCatchment {x} {y}')
	print(f'Start Process delineateCatchment {x} {y}')
	catchment = await catchment_from_coords(x,y)
	return catchment

@app.get("/wf-models/delineateCatchmentAsync")
async def delineateCatchmentAsync(x,y):
	logger.info(f'Start Process delineateCatchment {x} {y}')
	print(f'Start Process delineateCatchment {x} {y}')
	# resp = await catchment_from_coords_test(x,y)

	resp = await asyncio.gather(*[catchment_from_coords_test(x,y)])
	
	return resp

@app.get("/wf-models/raster_statistics")
def raster_result_statistics(usr_folder, intake_id,year, region):
	
	raster_list = preproc.rasters_statistics(usr_folder, intake_id,year, region)
	return raster_list

@app.get("/wf-models/tasks/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = validate_task_result(task_result)
    return JSONResponse(result)

@app.post("/wf-models/tasks", status_code=201)
def run_task(payload = Body(...)):
    task_type = payload["type"]
    task = create_task.delay(int(task_type))
    return JSONResponse({"task_id": task.id})

@app.post("/wf-models/task_catchment", status_code=201)
def task_catchment(payload = Body(...)):
		x = payload["x"]
		y = payload["y"]
		print(f'Start task_catchment {x} {y}')
		task = catchment_task.delay(x, y)
		print(f'Finish task_catchment {x} {y}')
		return JSONResponse({"task_id": task.id})

'''4. Invest Excecution'''
@app.post("/wf-models/task-exec-invest", status_code=201)
async def task_exec_invest(payload = Body(...)):
 	# (type:str,id_usuario:int, basin:int, case:int, models: List[str] = Query(None),catchment:List[int] = Query(None)):
	type = payload["type"]
	logger.info('Start Process ExecInvest from Task, Type: %s' % type)
	id_usuario = payload["id_usuario"]
	basin = payload["basin"]
	case = payload["case"]
	models = payload["models"]
	catchment = payload["catchment"]
	print (f'Start Process ExecInvest from Task, Type: {type}')
	task = exec_invest_task.delay(type,id_usuario, basin, case, models, catchment)
	print (f'Finish Process ExecInvest from Task, Type: {type}')
	return JSONResponse({"task_id": task.id})

async def catchment_from_coords(x,y):
	logger.info(f'Start Process catchment_from_coords {x} {y}')
	print(f'Start Process catchment_from_coords {x} {y}')
	dictResult = dict()
	dictResult['status'] = False
	try:
		x = float(x)
		y = float(y)
		basin = delineate.getRegionFromCoord(x,y)
		path = delineate.getPath(basin,1)
		catchment = delineate.delineateCatchment(path,x,y)
		dictResult = dict()
		dictResult['status'] = True
		dictResult['result'] = {}
		dictResult['result']['basin'] = basin
		dictResult['result']['geometry'] = catchment
	except Exception as e:
		dictResult['status'] = False
		dictResult['error'] = e.args
	logger.info(f'Successfull Execution catchment_from_coords {x} {y}')
	print (f'Successfull Execution catchment_from_coords: {x} {y}')
	return dictResult

async def catchment_from_coords_test(x,y):
	logger.info(f'Start Process catchment_from_coords {x} {y}')
	print(f'Start Process catchment_from_coords {x} {y}')
	dictResult = dict()
	dictResult['status'] = False
	dict_test = dict()
	for i in range(1,5):
		try:
			x = float(x)
			y = float(y)
			basin = delineate.getRegionFromCoord(x,y)
			path = delineate.getPath(basin,1)
			catchment = delineate.delineateCatchment(path,x,y)
			dictResult = dict()
			dictResult['status'] = True
			dictResult['result'] = {}
			dictResult['result']['basin'] = basin
			dictResult['result']['geometry'] = catchment
			dict_test[i] = dictResult
		except Exception as e:
			dictResult['status'] = False
			dictResult['error'] = e.args
			dict_test[i] = dictResult
	logger.info(f'Successfull Execution catchment_from_coords {x} {y}')
	print (f'Successfull Execution catchment_from_coords: {x} {y}')
	return dict_test
		
def validate_task_result(task_result):
    result = task_result.result
    status = task_result.status
    if status == 'FAILURE':
        result = 'Error'
    resp = {
        "task_id": task_result.id,
        "task_status": status,
        "task_result": result
    }
    return resp