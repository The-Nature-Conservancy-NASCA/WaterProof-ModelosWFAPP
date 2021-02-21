from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import delineate
from preproc import executeFunction,verifyExec,calcConc,calculateCarbonSum,InsertQualityParameters
import math
from aqueduct import cutAqueduct
from ptapSelection import getRandomLetter as grl
from getDataWB import generateAllData as InWB
from WI_Balance import execWB
from outWB import mergeData, readSum
from pydantic import BaseModel
from getDataPTAP import generateAll
from Select_PTAP import Select_PTAP
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
	try:
		result = generateAll(listcs.csinfras)
		r,awy = Select_PTAP("prueba")
		dictResult = dict()
		dictResult['estado'] = True
		dictResult['resultado'] = {
			"ptap_type":r,
			"awy":awy
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