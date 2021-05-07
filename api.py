from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from typing import List
import delineate
import math
import pathlib
import os
import shutil
import preproc
from datetime import datetime
from aqueduct import cutAqueduct
from ptapSelection import getRandomLetter as grl
from getDataWB import getDataDB
from getDataInWB import DataInWB, DataInWBPTAP, DataInBAU, DataInNBS, DataInBAUPTAP, DataInNBSPTAP
from WI_Balance import execWB
from outWB import mergeData, readSum, mergeDataPTAP, readSumPTAP
from outWBDisIntake import SaveInDB
from pydantic import BaseModel
from getDataPTAP import generateAll
from Select_PTAP import Select_PTAP
from reclassify import iterateFiles
import pandas as pd
import requests
from Disaggregation_WaterFunds.Disaggregation_and_Convolution import Desaggregation_BaU_NBS
import logging
import ptvsd

logger = logging.getLogger(__name__) # grabs underlying WSGI logger
logger.setLevel(logging.DEBUG)

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

@app.get("/")
async def root():
	logger.debug("Hello world")
	print("Hello world  with print")
	return {"message":"Hello World :: %s" % {__name__}}

 
@app.get("/snapPoint")
async def snap(x,y):
	dictResult = dict()
	dictResult['estado'] = False
	try:
		x = float(x)
		y = float(y)
		basin = delineate.getRegionFromCoord(x,y)
		path = delineate.getPath(basin,2)
		path = delineate.cutRaster(path,x,y,5)
		[x,y] = delineate.snap(path,x,y)
		dictResult = dict()
		dictResult['estado'] = True
		dictResult['resultado'] = {"x_snap":x,"y_snap":y}
	except Exception as e:
		dictResult['estado'] = False
		dictResult['error'] = e.args
	return dictResult
 
@app.get("/delineateCatchment")
async def delineateCatchment(x,y):
	dictResult = dict()
	dictResult['estado'] = False
	try:
		x = float(x)
		y = float(y)
		basin = delineate.getRegionFromCoord(x,y)
		path = delineate.getPath(basin,1)
		catchment = delineate.delineateCatchment(path,x,y)
		dictResult = dict()
		dictResult['estado'] = True
		dictResult['resultado'] = {}
		dictResult['resultado']['basin'] = basin
		dictResult['resultado']['geometry'] = catchment
	except Exception as e:
		dictResult['estado'] = False
		dictResult['error'] = e.args
	return dictResult

# def execInvest(type:str,id_usuario:int, basin:int,models: List[str] = Query(None),catchment:List[int] = Query(None)):
# 	execInv.delay(type,id_usuario,basin,models,catchment)
@app.get("/execInvest")
async def execInvest(type:str,id_usuario:int, basin:int, case:int, models: List[str] = Query(None),catchment:List[int] = Query(None)):
	print("execInvest start, Type: %s" % type)
	dictResult = dict()
	dictResult['estado'] = False
	catch = sorted(catchment,key=int)

	year = "0"
	if type == "BaU":
		year = preproc.analysisPeriodFromStudyCase(case)
		# 30  # TODO: get the true last year from case study analysis_period_value

	carbon = False
	# try:
	for i in catch:
		getDataDB( catch[i], "__wp_intake_emptycols" )

	for model in models:
		logger.debug("executeFunction for model :: %s" % {model})
		print(":: executeFunction for model :: %s" % {model})
		catchmentShp,path,label = preproc.executeFunction(basin,model,type,catchment,id_usuario, year)
		if (model == 'carbon'):
			carbon = True

	dictResult['resultado'] = 'successful execution for type :: {}'.format(type)

	dictResult['resultado'] = {}
	

	sum_carbon = -999 # TODO :: Validate if can be negative as disable value
	if (carbon):
		print ("Calculate carbon sum,")
		sum_carbon = preproc.calculateCarbonSum(catchmentShp,path,label)

	if(type == "quality" or type == "BaU"):
		execute = preproc.verifyExec(path)
		cont = 0
		dictResult['resultado'] = []
		for c in catch:
			
			s,n,p,q,sW,nW,pW = preproc.calcConc(execute,path,label,cont)
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
			
			preproc.InsertQualityParameters(c,'RIVER',q,sW,nW,pW,s,n,p)


			dictResult['resultado'].append({
				"catchment": c,
				"carbon" : sum_carbon,	
				"awy": q,
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
			})
			cont = cont + 1	
			
	# elif(type == "currentCarbon"):
	# 	sumCarbon = calculateCarbonSum(catchmentShp,path,label)
	# 	result = 0.0
	# 	dictResult['resultado'] = {
	# 		"carbon":sumCarbon
	# 	}

	elif type == "current":


		# Nothing ToDo, is equal to quality
		dictResult['resultado']=[]
		print (type)
		for c in catch:
			dictResult['resultado'].append({
					"catchment": c,
					"carbon" : sum_carbon,					
				})
		# dictResult['resultado'] = 'Ejecucion exitosa current scenario'

	# Revisar para solicitar como parámetro el ultimo año
	# TODO :: Revisar para implementar
	# elif type == "BaU":  
	#	dictResult['resultado'] = 'Ejecucion exitosa BaU'
	
	# TODO :: Revisar para implementar
	# Se ejecuta una vez x cada año
	# capa lulc tomada del resultado del traductor de cobertura	
	elif type == "NBS":  
		dictResult['resultado'] = 'Ejecucion exitosa NBS'


	dictResult['estado'] = True
	print(dictResult)

	# except Exception as e:
	# 	dictResult['estado'] = False
	# 	dictResult['error'] = e.args
	return dictResult

@app.get("/aqueduct")
async def calculateAqueduct(id_usuario,fecha):
	dictResult = dict()
	dictResult['estado'] = False
	try:
		list = cutAqueduct(id_usuario,fecha)
		print(list)
		dictResult = dict()
		dictResult['estado'] = True
		dictResult['resultado'] = list
	except Exception as e:
		dictResult['estado'] = False
		dictResult['error'] = e.args
	return dictResult

@app.post("/ptapSelection")
async def ptapSelect(listcs:ListCS):
	dictResult = dict()
	dictResult['estado'] = False
	# try:
	result = generateAll(listcs.csinfras)
	r,awy,cn,cp,cs,wn,wp,ws = Select_PTAP(result)
	dictResult = dict()
	dictResult['estado'] = True
	dictResult['resultado'] = {
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
	# 	dictResult['estado'] = False
	# 	dictResult['error'] = e.args
		
	return dictResult

# WB intake primera ejecucion tomando los valores de disaggregation
@app.get("/wbdisaggregationIntake")
async def calculateWBDisaggregationIntake(id_intake,user_id,study_case_id):
	function_db = "__wp_intake_insert_report"
	dictResult = dict()
	dictResult['estado'] = False
	# try:
	DataInBAU(id_intake)
	execWB()
	SaveInDB( function_db, id_intake, user_id, study_case_id, "BAU" )
	DataInNBS(id_intake)
	execWB()
	SaveInDB( function_db, id_intake, user_id, study_case_id, "NBS" )
	dictResult = dict()
	dictResult['estado'] = True
	dictResult['resultado'] = {"result":'Transacción exitosa'}
	# except Exception as e:
	# 	dictResult['estado'] = False
	# 	dictResult['error'] = e.args
	return dictResult

# WB PTAP primera ejecucion tomando los valores de disaggregation
@app.get("/wbdisaggregationPTAP")
async def calculateWBDisaggregationPTAP(ptap_id,user_id,study_case_id):
	function_bd = '__wp_ptap_insert_report'
	dictResult = dict()
	dictResult['estado'] = False
	# try:
	DataInBAUPTAP(ptap_id)
	execWB()
	SaveInDB( function_bd, ptap_id, user_id, study_case_id, 'BAU' )
	DataInNBSPTAP(ptap_id)
	execWB()
	SaveInDB( function_bd, ptap_id, user_id, study_case_id, 'NBS' )
	dictResult = dict()
	dictResult['estado'] = True
	dictResult['resultado'] = {"result":'Transacción exitosa'}
	# except Exception as e:
	# 	dictResult['estado'] = False
	# 	dictResult['error'] = e.args
	return dictResult

#water balance segunda ejecucion
@app.get("/wb")
async def calculateWB(id_intake):
	dictResult = dict()
	dictResult['estado'] = False
	try:
		DataInWB(id_intake)
		execWB()
		outFile = mergeData()
		readSum(outFile)
		dictResult = dict()
		dictResult['estado'] = True
		dictResult['resultado'] = {"result":'Transacción exitosa'}
	except Exception as e:
		dictResult['estado'] = False
		dictResult['error'] = e.args
	return dictResult

@app.get("/wbPTAP")
async def calculateWBPTAP(id_ptap):
	dictResult = dict()
	dictResult['estado'] = False
	# try:
	ptap_id = int(id_ptap)
	DataInWBPTAP(ptap_id)
	execWB()
	outFile = mergeDataPTAP()
	readSumPTAP(outFile)
	dictResult['estado'] = True
	dictResult['resultado'] = {"result":'Transacción exitosa'}
	# except Exception as e:
	# 	dictResult['estado'] = False
	# 	dictResult['error'] = e.args
	return dictResult

@app.get("/cobTrans")
async def cobTrans(pathCobs,nbs_id,pathLULC):
	print ("cobTrans :: start")
	dictResult = dict()
	dictResult['estado'] = True
	try:
		paths = iterateFiles(pathCobs,nbs_id,pathLULC)		
		dictResult['resultado'] = {"result":'successful execution'}
		dictResult['paths'] = paths
	except Exception as e:
		dictResult['estado'] = False
		dictResult['error'] = "Everything that could fail, failed!!!"

	return dictResult


@app.get("/disaggregation")
async def disaggregation(user_id):
	
	query = {'type':'quality', 'id_usuario':'1', 'basin' : '44', 'models' : 'sdr', 'catchment' : '1', 'models' : 'amy', 'models' : 'ndr'}
	print (query)
	
	api_url = "http://dev.skaphe.com:8000/execInvest"
	response = requests.get(api_url, params=query)
	print(response.json())
	return response.json()
	
	in_invest = '01-INPUTS_InVEST.csv'
	in_nbs    = '01-INPUTS_NBS.csv'
	in_time   = '01-INPUTS_Time.csv'
	out_bau = '02-OUTPUTS_BaU.csv'
	out_nbs = '02-OUTPUTS_NBS.csv'
	DISAGGREGATION = 'DISAGGREGATION'
	name_cols = ['AWY (m3)','Wsed (Ton)','WN (Kg)','WP (kg)','BF (m3)','WC (Ton)']
	current_dir = pathlib.Path().absolute()
	demo_data = "/Disaggregation_WaterFunds/Project"
	path_data = str(current_dir) + demo_data
	Desaggregation_BaU_NBS(path_data, path_data)

	dict_result = dict()
	dict_result['status'] = True
    
	dict_result['nbs'] = pd.read_csv(os.path.join(path_data, out_nbs),usecols=name_cols)
	dict_result['bau'] = pd.read_csv(os.path.join(path_data, out_bau),usecols=name_cols)

	PATH_FILES = os.environ["PATH_FILES"]
	date_ymd = datetime.today().strftime('%Y-%m-%d')
	user_dir = user_id + '_' + date_ymd
	path = os.path.join(PATH_FILES,'salidas', user_dir)
	validate_and_create_dir (path)
	path_out_in = os.path.join(path,'in')
	validate_and_create_dir (path_out_in)	
	path_in_dissagregation = os.path.join(path_out_in, DISAGGREGATION)
	validate_and_create_dir (path_in_dissagregation)

	path_out_out = os.path.join(path,'out')
	validate_and_create_dir (path_out_out)
	path_out_dissagregation = os.path.join(path_out_out, DISAGGREGATION)
	validate_and_create_dir (path_out_dissagregation)

	dict_result["output"] = {}
	dict_result["output"]["user_dir"] = user_dir
	dict_result["output"]["topic"] = DISAGGREGATION
	dict_result["output"]["files"] = [out_bau, out_nbs]	 
	base_url = "/download?user_dir=" + user_dir + "&topic="+DISAGGREGATION + "&file="
	dict_result["output"]["urls"] = [base_url + out_bau, base_url + out_nbs]

	print ("export inputs to: " + path_in_dissagregation)
	shutil.copyfile(os.path.join(path_data,in_invest), os.path.join(path_in_dissagregation,in_invest))
	shutil.copyfile(os.path.join(path_data,in_nbs), os.path.join(path_in_dissagregation,in_nbs))
	shutil.copyfile(os.path.join(path_data,in_time), os.path.join(path_in_dissagregation,in_time))

	print ("export outputs to: " + path_out_dissagregation)
	shutil.copyfile(os.path.join(path_data,out_bau), os.path.join(path_out_dissagregation,out_bau))
	shutil.copyfile(os.path.join(path_data,out_nbs), os.path.join(path_out_dissagregation,out_nbs))
	return dict_result

@app.get("/disaggregation2")
def disaggregation2(user_id, study_cases_id):

	return preproc.processDissagregation(user_id, study_cases_id)

@app.get("/roiExecution")
def roiExecution(user_id, study_cases_id):

	return preproc.processRoi(user_id,study_cases_id)

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
