from fastapi import FastAPI, Query
from typing import List
import delineate
from preproc import executeFunction,verifyExec,calcConc,calculateCarbonSum

app = FastAPI()

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
	except:
		dictResult['estado'] = False
		dictResult['error'] = print("Error en la ejeucion")
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
		dictResult['resultado'] = catchment
	except:
		dictResult['estado'] = False
		dictResult['error'] = print("Error en la ejecucion")
	return dictResult

@app.get("/execInvest")
async def execInvest(type:str,id_usuario:int, basin:int,catchment:int,models: List[str] = Query(None)):
	dictResult = dict()
	dictResult['estado'] = False

	try:
		for model in models:
			catchmentShp,path,label = executeFunction(basin,model,type,catchment,id_usuario)

		dictResult['resultado'] = 'Ejecucion exitosa'

		if(type == "quality"):
			execute = verifyExec(path)
			s,n,p = calcConc(execute,path,label)
			dictResult['resultado'] = {
				"sediment":s,
				"nitrogen":n,
				"phosporus":p
			}		
		elif(type == "currentCarbon"):
			sumCarbon = calculateCarbonSum(catchmentShp,path,label)
			dictResult['resultado'] = {
				"carbon":sumCarbon
			}	
		dictResult['estado'] = True

	except Exception as e:
		dictResult['estado'] = False
		dictResult['error'] = e.args
	return dictResult