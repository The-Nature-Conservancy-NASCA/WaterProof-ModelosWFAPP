import sys
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

def reclassify(listTrans):
    driver = gdal.GetDriverByName('GTiff')
    file = gdal.Open('activity_portfolio_continuous_year_1.tif')
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

    # create new file
    file2 = driver.Create('raster2.tif', file.RasterXSize , file.RasterYSize , 1)
    file2.GetRasterBand(1).WriteArray(lista)

    # spatial ref system
    proj = file.GetProjection()
    georef = file.GetGeoTransform()
    file2.SetProjection(proj)
    file2.SetGeoTransform(georef)
    file2.FlushCache()


listTransformations = getTranformations(5)
reclassify(listTransformations)
print(listTransformations)



