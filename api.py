from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import delineate
from preproc import executeFunction,verifyExec,calcConc,calculateCarbonSum
import math
from aqueduct import cutAqueduct

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

@app.get("/execInvest")
async def execInvest(type:str,id_usuario:int, basin:int,models: List[str] = Query(None),catchment:List[int] = Query(None)):
	dictResult = dict()
	dictResult['estado'] = False
	catch = sorted(catchment,key=int)

	try:
		for model in models:
			catchmentShp,path,label = executeFunction(basin,model,type,catchment,id_usuario)

		dictResult['resultado'] = 'Ejecucion exitosa'

		if(type == "quality"):
			execute = verifyExec(path)
			cont = 0
			dictResult['resultado'] = []
			for c in catch:
				s,n,p = calcConc(execute,path,label,cont)
				if math.isnan(s):
					s = 0
				elif math.isnan(n):
					n = 0
				elif math.isnan(p):
					p = 0

				dictResult['resultado'].append({
					"catchment": c,
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

		dictResult['estado'] = True
		print(dictResult)

	except Exception as e:
		dictResult['estado'] = False
		dictResult['error'] = e.args
	return dictResult

@app.get("/aqueduct")
async def calculateAqueduct(id_usuario,fecha):
	dictResult = dict()
	dictResult['estado'] = False
	# try:
	list = cutAqueduct(id_usuario,fecha)
	print(list)
	dictResult = dict()
	dictResult['estado'] = True
	dictResult['resultado'] = list
	# except Exception as e:
	# 	dictResult['estado'] = False
	# 	dictResult['error'] = e.args
	return dictResult