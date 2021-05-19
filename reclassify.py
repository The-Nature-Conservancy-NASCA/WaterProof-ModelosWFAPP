import sys,os,json
from osgeo import gdal
from pathlib import Path
sys.path.append('config')
from config import config
from connect import connect

def readJsonActivities(path):
    p = Path(path).parents[0]
    pathJson = os.path.join(p,'activity_raster_id.json')
    f = open(pathJson) 
    jsonFile = json.load(f)
    dictIds = {}

    for key in jsonFile:
        dictIds[jsonFile[key]['index']] = key

    return dictIds


def getTranformations_by_id(id):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('__wp_gettransformationsById',[id])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult


def getTranformations_by_name(name):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('__wp_gettransformationsByName',[name])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def reclassify(pathFile,outPath,filename,lulc_path,json):
    driver = gdal.GetDriverByName('GTiff')
    file = gdal.Open(pathFile)
    file_lulc = gdal.Open(lulc_path)
    band = file.GetRasterBand(1)
    band_lulc = file_lulc.GetRasterBand(1)
    lista = band.ReadAsArray()
    lista_lulc = band_lulc.ReadAsArray()
    lulc_positions = []

    # print(lista)

    transformations = {}

    for j in range(file.RasterXSize):
        for i in  range(file.RasterYSize):
            # print(lista[i,j])
            indice = lista[i,j]

            if indice != 255:
                sbn = json[indice]
                if not sbn in transformations:
                    transformations[sbn] = getTranformations_by_name(sbn) 

                for x in transformations[sbn]:
                    # print("Lista "+ str(lista_lulc[i,j]))
                    # print("X 0 " + str(x[0]))
                    if lista_lulc[i,j] == x[0]:
                        lista_lulc[i,j] = x[2]
                        break            
           
    pathTranslated = os.path.join(outPath,filename)
    # create new file
    file2 = driver.Create(pathTranslated, file_lulc.RasterXSize , file_lulc.RasterYSize , 1)
    file2.GetRasterBand(1).WriteArray(lista_lulc)
    file2.GetRasterBand(1).SetNoDataValue(255)

    # spatial ref system
    proj = file.GetProjection()
    georef = file.GetGeoTransform()
    file2.SetProjection(proj)
    file2.SetGeoTransform(georef)
    file2.FlushCache()
    return pathTranslated

def iterateFiles(path,lulc_path):
    
    pathOut = os.path.join(path,"translated_cob")
    json = readJsonActivities(path)

    if not os.path.isdir(pathOut):
        os.mkdir(pathOut)

    paths = []
    for filename in os.listdir(path):
        if filename.endswith(".tif"):
            path_file = reclassify(os.path.join(path,filename),pathOut,filename,lulc_path,json)
            paths.append(path_file)

    return paths

# readJsonActivities('/home/skaphe/Documentos/tnc/modelos/salidas/9_2020_10_24/out/04-RIOS/1_investment_portfolio_adviser_workspace/activity_portfolios/continuous_activity_portfolios')
# iterateFiles('/home/skaphe/Documentos/tnc/modelos/salidas/9_2020_10_24/out/04-RIOS/1_investment_portfolio_adviser_workspace/activity_portfolios/continuous_activity_portfolios',5,'/home/skaphe/Documentos/tnc/modelos/salidas/9_2020_10_24/in/04-RIOS/LULC_SA_1.tif')
# reclassify(listTransformations)
# print(listTransformations)



