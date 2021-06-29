import sys,os,json
from osgeo import gdal
from pathlib import Path
sys.path.append('config')
from config import config
from connect import connect
from osgeo import gdal
from os import environ,path
import constants

base_path = environ["PATH_FILES"]

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

def reclassify(pathFile,outPath,filename,lulc_path,json, is_future, future_lulc_path):
    driver = gdal.GetDriverByName('GTiff')
    file = gdal.Open(pathFile)
    file_lulc = gdal.Open(lulc_path)
    band = file.GetRasterBand(1)
    band_lulc = file_lulc.GetRasterBand(1)
    lista = band.ReadAsArray()
    lista_lulc = band_lulc.ReadAsArray()
    
    if (is_future):
        file_future_lulc = gdal.Open(future_lulc_path)
        band_future_lulc = file_future_lulc.GetRasterBand(1)
        lista_future_lulc = band_future_lulc.ReadAsArray()

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
                        if (is_future):
                            lista_future_lulc[i,j] = x[2]
                        else:    
                            lista_lulc[i,j] = x[2]
                        break            
           
    pathTranslated = os.path.join(outPath,filename)
    # create new file
    file2 = driver.Create(pathTranslated, file_lulc.RasterXSize , file_lulc.RasterYSize , 1)
    if (is_future):
        file2.GetRasterBand(1).WriteArray(lista_future_lulc)
    else:
        file2.GetRasterBand(1).WriteArray(lista_lulc)
    file2.GetRasterBand(1).SetNoDataValue(255)

    # spatial ref system
    proj = file.GetProjection()
    georef = file.GetGeoTransform()
    file2.SetProjection(proj)
    file2.SetGeoTransform(georef)
    file2.FlushCache()
    return pathTranslated

def reclassifyFilesInFolder(path,lulc_path, is_future, future_lulc_path, year, region):
    print ("reclassifyFilesInFolder")
    print ("path : %s", path)
    print ("lulc_path : %s", lulc_path)
    print ("is_future %s", is_future)
    print ("future_lulc_path %s", future_lulc_path)
    print ("year: %s", year)
    print ("region: %s" % region)

    pathOut = os.path.join(path,"translated_cob")
    json = readJsonActivities(path)

    if not os.path.isdir(pathOut):
        os.mkdir(pathOut)

    paths = []
    TIF_EXT = '.tif'
    FUTURE_TIF_SUFFIX = '_FUTURE.tif'
    FUTURE_COMPLETE_TIF_SUFFIX = '_FUTURE_COMPLETE.tif'
    
    for filename in os.listdir(path):
        if filename.endswith(TIF_EXT):
            out_filename = filename
            if (is_future):
                out_filename = filename.replace(TIF_EXT, FUTURE_TIF_SUFFIX)
            path_file = reclassify(os.path.join(path,filename),pathOut,out_filename,lulc_path,json, is_future, future_lulc_path)
            if (is_future):
                lulc_path_region = '%s/%s/%s/YEAR_%s/LULC_%s.tif' % (base_path, constants.IN_BASE_DIR ,constants.LANDCOVER_DIR,year,region)
                print ("lulc_path_region : %s" % lulc_path_region)
                lulc_path_complete = os.path.join(pathOut,filename.replace(TIF_EXT, FUTURE_COMPLETE_TIF_SUFFIX))
                print ("lulc_path_complete : %s" % lulc_path_complete)
                command = "gdal_merge.py -o %s -of gtiff %s %s" % (lulc_path_complete, lulc_path_region, path_file)
                print(os.popen(command).read())
            paths.append(path_file)

    return paths

# readJsonActivities('/home/skaphe/Documentos/tnc/modelos/salidas/9_2020_10_24/out/04-RIOS/1_investment_portfolio_adviser_workspace/activity_portfolios/continuous_activity_portfolios')
# reclassifyFilesInFolder('/home/skaphe/Documentos/tnc/modelos/salidas/9_2020_10_24/out/04-RIOS/1_investment_portfolio_adviser_workspace/activity_portfolios/continuous_activity_portfolios',5,'/home/skaphe/Documentos/tnc/modelos/salidas/9_2020_10_24/in/04-RIOS/LULC_SA_1.tif')
# reclassify(listTransformations)
# print(listTransformations)



