from celery import Celery
from celery.utils.log import get_task_logger

# Create the celery app and get the logger
celery_app = Celery('tasks', broker='pyamqp://guest@rabbit//')
logger = get_task_logger(__name__)


# @celery_app.task
# def execInv(type,id_usuario,basin,models,catchment):
#     dictResult = dict()
# 	dictResult['estado'] = False
# 	catch = sorted(catchment,key=int)

# 	try:
# 		for model in models:
# 			catchmentShp,path,label = executeFunction(basin,model,type,catchment,id_usuario)

# 		dictResult['resultado'] = 'Ejecucion exitosa'

# 		if(type == "quality"):
# 			execute = verifyExec(path)
# 			cont = 0
# 			dictResult['resultado'] = []
# 			for c in catch:
# 				s,n,p,q,sW,nW,pW = calcConc(execute,path,label,cont)
# 				if math.isnan(s):
# 					s = 0
# 				elif math.isnan(n):
# 					n = 0
# 				elif math.isnan(p):
# 					p = 0
# 				elif math.isnan(q):
# 					q = 0
# 				elif math.isnan(sW):
# 					sW = 0
# 				elif math.isnan(nW):
# 					nW = 0
# 				elif math.isnan(pW):
# 					pW = 0

				
# 				InsertQualityParameters(c,'RIO',q,sW,nW,pW,s,n,p)


# 				dictResult['resultado'].append({
# 					"catchment": c,
# 					"awy": q,
# 					"w": {
# 						"sediment":sW,
# 						"nitrogen":nW,
# 						"phosporus":pW
# 					},
# 					"concentrations": {
# 					"sediment":s,
# 					"nitrogen":n,
# 					"phosporus":p
# 				}
# 				})
# 				cont = cont + 1	

				
# 		elif(type == "currentCarbon"):
# 			sumCarbon = calculateCarbonSum(catchmentShp,path,label)
# 			result = 0.0
# 			dictResult['resultado'] = {
# 				"carbon":sumCarbon
# 			}

# 		dictResult['estado'] = True
# 		print(dictResult)

# 	except Exception as e:
# 		dictResult['estado'] = False
# 		dictResult['error'] = e.args
# 	return dictResult