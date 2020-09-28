# Date: 24/09/2020
# Author: Diego Rodriguez - Skaphe Tecnologia SAS
# WFApp


# Importacion de librerias
import sys
import os.path
from os import path
import rasterio
sys.path.append('config')
from connect import connect

# Cortar raster
def cutRaster(catchment,path):
	data = rasterio.open(path)
	print(data)


# Recuperar macroregion por id
def getRegionFromId(basin):
	result = ''
	cursor = connect('postgresql').cursor()
	cursor.callproc('getBasin',[basin])
	result = cursor.fetchall()
	for row in result:
		result = row
	cursor.close()
	return result
 
# Recuperar constante por macroregion
def getConstantFromBasin(basin,constantName):
	result = ''
	cursor = connect('postgresql_alfa').cursor()
	cursor.callproc('wfa.getconstant',[basin,constantName])
	result = cursor.fetchall()
	for row in result:
		result = row
	cursor.close()
	return result

# Obtener parametros de modelo
def getParameters(basin,model):
	result = ''
	listResult = []
	cursor = connect('postgresql_alfa').cursor()
	cursor.callproc('wfa.getparametersmodel',[basin,model])
	result = cursor.fetchall()
	for row in result:
		listResult.append(row)
	cursor.close()
	return listResult
 
# Procesar parametros
def processParameters(parametersList, basin):
	dictParameters = dict()
	catchment = 'catchment.shp'
	for parameter in parametersList:
		name = parameter[0]
		value = parameter[1]
		if(value == 'False'):
			value = False
		elif(value == 'True'):
			value = False		
		cut = parameter[2]
		constant = parameter[3]
		suffix = parameter[4]
		empty = parameter[5]
		if(suffix):
			region = getRegionFromId(basin)
			label = region[4]
			value = label
		if(constant):
			constantValue = getConstantFromBasin(basin,name)
			value = constantValue[2]
		if(empty):
			value = ''
		if(cut):
			cutRaster(catchment,value)
		dictParameters[name] = value
	print(dictParameters)
	return dictParameters
 
list = getParameters(44,'awy')
dict = processParameters(list,44)
#cutRaster('aaaaa',dict)