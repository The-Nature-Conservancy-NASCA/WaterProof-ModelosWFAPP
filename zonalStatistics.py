from rasterstats import zonal_stats
import os
import csv

def calculateStatistic(types,raster,catchment):
	print ("calculateStatistic")
	stats = zonal_stats(catchment,raster,stats=types,all_touched=True)
	return stats
 
def calculateRainfallDayMonth(folder,catchment,label):
	print ("calculateRainfallDayMonth")
	months = dict()
	months['JAN'] = 1
	months['FEB'] = 2
	months['MAR'] = 3
	months['APR'] = 4
	months['MAY'] = 5
	months['JUN'] = 6
	months['JUL'] = 7
	months['AGO'] = 8
	months['SEP'] = 9
	months['OCT'] = 10
	months['NOV'] = 11
	months['DEC'] = 12
	typeStat = ['mean']

	rainfallList = []


	for filename in os.listdir(folder):
		
		if filename.endswith(".tif") and label in filename:		
			#print(filename)	
			monthName = filename.split("_")[1]
			monthNumber = months[monthName]
			fileRaster = os.path.join(folder,filename)
			print("calculateStatistic for %s" % monthName)
			zs = calculateStatistic(typeStat,fileRaster,catchment)
			result = zs[0]
			print("shp: %s :: raster: %s, zs: %s" % (catchment, fileRaster, zs))
			rainfallList.append([monthNumber,int(result[typeStat[0]])])
		
	# print(rainfallList)
	return rainfallList
 
def saveCsv(headers,content,folder):
	row_list = []
	row_list.append(headers)

	for item in content:
		row_list.append([item[0],item[1]])
	
	with open(os.path.join(folder,"rainfall_day.csv"),"w",newline='') as file:
		writer = csv.writer(file)
		writer.writerows(row_list)
			
			
			
      
#list = calculateRainfallDayMonth("/home/skaphe/Documentos/tnc/modelos/entradas/14-Day_Rainfall/","/home/skaphe/Documentos/tnc/modelos/Workspace_BasinDelineation/tmp/1_2020_10_3/in/catchment/catchment.shp","SA_1")
#saveCsv(['month','events'],list,os.getcwd())
   
#calculateStatistic(['mean'],"/home/skaphe/Documentos/tnc/modelos/entradas/03-LandCover/YEAR_0/LULC_SA_1.tif","/home/skaphe/Documentos/tnc/modelos/Workspace_BasinDelineation/tmp/1_2020_10_3/in/catchment/catchment.shp")