import sys,os
from osgeo import gdal
sys.path.append('config')
from config import config
from connect import connect



def getTranformations(nbs_id):
    result = ''
    listResult = []
    conn = connect('postgresql_alfa')
    cursor = conn.cursor()
    cursor.callproc('gettransformations',[nbs_id])
    result = cursor.fetchall()
    for row in result:
        listResult.append(row)
    cursor.close()
    conn.close()
    return listResult

def reclassify(listTrans,pathFile,outPath,filename):
    driver = gdal.GetDriverByName('GTiff')
    file = gdal.Open(pathFile)
    band = file.GetRasterBand(1)
    lista = band.ReadAsArray()
    for x in listTrans:
        print(x[0])
        print(x[2])
    # reclassification
        for j in  range(file.RasterXSize):
            for i in  range(file.RasterYSize):
                # print(lista[i,j])
                if lista[i,j] == x[0]:
                    lista[i,j] = x[2]

    pathTranslated = os.path.join(outPath,filename)
    # create new file
    file2 = driver.Create(pathTranslated, file.RasterXSize , file.RasterYSize , 1)
    file2.GetRasterBand(1).WriteArray(lista)

    # spatial ref system
    proj = file.GetProjection()
    georef = file.GetGeoTransform()
    file2.SetProjection(proj)
    file2.SetGeoTransform(georef)
    file2.FlushCache()

def iterateFiles(path,nbs_id):
    listTransformations = getTranformations(nbs_id)
    pathOut = os.path.join(path,"translated_cob")

    if not os.path.isdir(pathOut):
        os.mkdir(pathOut)

    for filename in os.listdir(path):
        if filename.endswith(".tif"):
            reclassify(listTransformations,os.path.join(path,filename),pathOut,filename)



iterateFiles('/home/skaphe/Documentos/tnc/modelos/salidas/9_2020_10_24/out/04-RIOS/1_investment_portfolio_adviser_workspace/activity_portfolios/continuous_activity_portfolios',5)
# reclassify(listTransformations)
# print(listTransformations)



