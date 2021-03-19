from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import delineate
import math
import pathlib
import os
import shutil
from datetime import datetime
from preproc import executeFunction,verifyExec,calcConc,calculateCarbonSum,InsertQualityParameters
from aqueduct import cutAqueduct
from ptapSelection import getRandomLetter as grl
from getDataWB import generateAllData as InWB
from getDataWBPTAP import generateAllData as InWBPTAP
from WI_Balance import execWB
from outWB import mergeData, readSum, mergeDataPTAP, readSumPTAP
from pydantic import BaseModel
from getDataPTAP import generateAll
from Select_PTAP import Select_PTAP
from reclassify import iterateFiles
import pandas as pd
from Disaggregation_WaterFunds.Disaggregation_and_Convolution import Desaggregation_BaU_NBS
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
	return {"message":"Hello World"}
 
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
async def execInvest(type:str,id_usuario:int, basin:int,models: List[str] = Query(None),catchment:List[int] = Query(None)):
	dictResult = dict()
	dictResult['estado'] = False
	catch = sorted(catchment,key=int)

	# try:
	for model in models:
		catchmentShp,path,label = executeFunction(basin,model,type,catchment,id_usuario)

	dictResult['resultado'] = 'Ejecucion exitosa'

	if(type == "quality"):
		execute = verifyExec(path)
		cont = 0
		dictResult['resultado'] = []
		for c in catch:
			s,n,p,q,sW,nW,pW = calcConc(execute,path,label,cont)
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

			
			InsertQualityParameters(c,'RIVER',q,sW,nW,pW,s,n,p)


			dictResult['resultado'].append({
				"catchment": c,
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

			
	elif(type == "currentCarbon"):
		sumCarbon = calculateCarbonSum(catchmentShp,path,label)
		result = 0.0
		dictResult['resultado'] = {
			"carbon":sumCarbon
		}

	elif type == "current":
		dictResult['resultado'] = 'Ejecucion exitosa current scenario'


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
	print(listcs.csinfras)
	try:
		result = generateAll(listcs.csinfras)
		print(result)
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
	except Exception as e:
		dictResult['estado'] = False
		dictResult['error'] = e.args
		
	return dictResult

@app.get("/wb")
async def calculateWB(id_intake):
	dictResult = dict()
	dictResult['estado'] = False
	# try:
	InWB(id_intake)
	execWB()
	outFile = mergeData()
	readSum(outFile)
	dictResult = dict()
	dictResult['estado'] = True
	dictResult['resultado'] = {"result":'Transacción exitosa'}
	# except Exception as e:
	# 	dictResult['estado'] = False
	# 	dictResult['error'] = e.args
	return dictResult

@app.get("/wbPTAP")
async def calculateWBPTAP(id_ptap):
	dictResult = dict()
	dictResult['estado'] = False
	# try:
	ptap_id = int(id_ptap)
	InWBPTAP(ptap_id)
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
	dictResult = dict()

	try:
		iterateFiles(pathCobs,5,pathLULC)
		dictResult['estado'] = True
		dictResult['resultado'] = {"result":'Transacción exitosa'}
	except Exception as e:
		dictResult['estado'] = False
		dictResult['error'] = "Todo lo que podia fallar falló!!!!"

	return dictResult


@app.get("/disaggregation")
async def disaggregation(user_id):
	
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
	Desaggregation_BaU_NBS(path_data)

	dict_result = dict()
	dict_result['status'] = True
    
	dict_result['nbs'] = pd.read_csv(os.path.join(path_data, out_nbs),usecols=name_cols)
	dict_result['bau'] = pd.read_csv(os.path.join(path_data, out_bau),usecols=name_cols)

	PATH_FILES = os.environ["PATH_FILES"]
	date_ymd = datetime.today().strftime('%Y-%m-%d')
	path = os.path.join(PATH_FILES,'salidas', user_id + '_' + date_ymd)
	validate_and_create_dir (path)
	path_out_in = os.path.join(path,'in')
	validate_and_create_dir (path_out_in)	
	path_in_dissagregation = os.path.join(path_out_in, DISAGGREGATION)
	validate_and_create_dir (path_in_dissagregation)

	path_out_out = os.path.join(path,'out')
	validate_and_create_dir (path_out_out)
	path_out_dissagregation = os.path.join(path_out_out, DISAGGREGATION)
	validate_and_create_dir (path_out_dissagregation)

	print ("export inputs to: " + path_in_dissagregation)
	shutil.copyfile(os.path.join(path_data,in_invest), os.path.join(path_in_dissagregation,in_invest))
	shutil.copyfile(os.path.join(path_data,in_nbs), os.path.join(path_in_dissagregation,in_nbs))
	shutil.copyfile(os.path.join(path_data,in_time), os.path.join(path_in_dissagregation,in_time))

	print ("export outputs to: " + path_out_dissagregation)
	shutil.copyfile(os.path.join(path_data,out_bau), os.path.join(path_out_dissagregation,out_bau))
	shutil.copyfile(os.path.join(path_data,out_nbs), os.path.join(path_out_dissagregation,out_nbs))
	return dict_result

def validate_and_create_dir(dir_to_validate):

	if(not os.path.isdir(dir_to_validate)):
		os.mkdir(dir_to_validate)
