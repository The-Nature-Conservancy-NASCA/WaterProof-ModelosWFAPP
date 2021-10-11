import os
import time
import logging
import delineate

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