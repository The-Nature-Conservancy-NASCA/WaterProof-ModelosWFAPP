import os
import time
import logging
import delineate

from typing import List
from ROIFunctions.common_functions import updateDataDB
import preproc
import constants


from celery import Celery

logger = logging.getLogger(__name__) # grabs underlying WSGI logger
logger.setLevel(logging.DEBUG)

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="create_task", queue="worker_invest")
def create_task(task_type):
  time.sleep(int(task_type) * 10)
  return True

@celery.task(name="catchment_task", queue="worker_invest")
def catchment_task(x,y):  
  logger.info(f'Start Process catchment_from_coords {x} {y}')
  print(f'pr-Start Process catchment_from_coords {x} {y}')
  dictResult = dict()
  dictResult['status'] = False
  dict_test = dict()
  for i in range(1,10):
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
  print (f'pr-Successfull Execution catchment_from_coords: {x} {y}')
  # print (dict_test)
  return dict_test

@celery.task(name="exec_invest_task", queue="worker_invest")
def exec_invest_task(type:str,id_usuario:int, basin:int, case:int, models: List[str],catchment:List[int]):
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
			model_dir = '03-INVEST'

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