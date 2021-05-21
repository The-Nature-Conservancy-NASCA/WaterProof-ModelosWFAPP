from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from typing import List
import delineate
import math
import pathlib
import os
from os import environ,path
import shutil
import preproc
from datetime import datetime
from aqueduct import cutAqueduct
from ptapSelection import getRandomLetter as grl
from getDataWB import getDataDB, updateDataDB
from getDataInWB import DataInWB, DataInWBPTAP, DataInBAU, DataInNBS, DataInBAUPTAP, DataInNBSPTAP
from WI_Balance import execWB
from outWB import mergeData, readSum, mergeDataPTAP, readSumPTAP
from outWBDisIntake import SaveInDB
from pydantic import BaseModel
from getDataPTAP import generateAll
from Select_PTAP import Select_PTAP
from reclassify import iterateFiles
from dissagregation import DataCSVDis
import pandas as pd
import requests
from Disaggregation_WaterFunds.Disaggregation_and_Convolution import Desaggregation_BaU_NBS
import logging
import ptvsd

ruta = environ["PATH_FILES"]
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
		dictResult['basin'] = basin
		path = delineate.getPath(basin,2)
		dictResult['path'] = path
		path = delineate.cutRaster(path,x,y,5)
		dictResult['path_raster'] = path
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
	updateDataDB( catch[0], "__wp_intake_emptycols" )
	year = "0"
	if type == "BaU" or type == "NBS": # TODO: Para current tambien se necesita
		year = preproc.analysisPeriodFromStudyCase(case)
		# 30  # TODO: get the true last year from case study analysis_period_value (done)
	elif type == "current":
		year = 0
	carbon = False
	# try:
	
	model_dir = '01-INVEST_QUALITY';
	year_dir = 'YEAR_' + str(year)
	if(type != "quality"):
		model_dir = '03-INVEST';

	for model in models:
		#logger.debug("executeFunction for model :: %s" % {model})
		#print(":: executeFunction for model :: %s" % {model})
		if type == "NBS":
			for x in range(0,year):
				print(":: executeFunction model %s , Type: NBS for Year :: %s of %s" % (model, x, year))
				catchmentShp,path,label = preproc.executeFunction(basin,model,type,catchment,id_usuario, x, case)
		else:
			catchmentShp,path,label = preproc.executeFunction(basin,model,type,catchment,id_usuario, year, case)
		if (model == 'carbon'):
			carbon = True

	dictResult['resultado'] = 'successful execution for type :: {}'.format(type)

	dictResult['resultado'] = {}

	sum_carbon = -999 # TODO :: Validate if can be negative as disable value
	if (carbon):
		print ("Calculate carbon sum,")
		sum_carbon = preproc.calculateCarbonSum(catchmentShp,path,label, model_dir, year_dir)
	
	if(type == "quality" or type == "BaU"):
		execute = preproc.verifyExec(path, model_dir)
		cont = 0
		dictResult['resultado'] = []
		for c in catch:
			s,n,p,q,sW,nW,pW,bf = preproc.calcConc(execute,path,label,cont, model_dir, year_dir)
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
			preproc.insertInvestResult(year,type,q,nW,pW,sW,bf,sum_carbon[0]['sum'],c, case, id_usuario)
			
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
async def cobTrans(pathCobs,pathLULC):
	print ("cobTrans :: start")
	dictResult = dict()
	dictResult['estado'] = True
	try:
		paths = iterateFiles(pathCobs,pathLULC)		
		dictResult['resultado'] = {"result":'successful execution'}
		dictResult['paths'] = paths
	except Exception as e:
		dictResult['estado'] = False
		dictResult['error'] = "Everything that could fail, failed!!!"

	return dictResult


@app.get("/disaggregation")
async def disaggregation( id_usuario, basin, case, catchment):

	path_data_in = path.join( ruta, "salidas", "disaggregation", "INPUTS" )
	path_data_out = path.join( ruta, "salidas", "disaggregation", "Out" )

	dict_result = dict()
	dict_result['status'] = True
    # try:
	DataCSVDis(catchment, case)
	Desaggregation_BaU_NBS(path_data_in, path_data_out)
	# except Exception as e:
	# 	dictResult['estado'] = False
	# 	dictResult['error'] = e.args
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
