# Date: 10/09/2020
# Author: Diego Rodriguez - Skaphe Tecnologia SAS
# WFApp


# Importacion de librerias
import sys, os
from pysheds.grid import Grid
import fiona
import argparse
import math
import rasterio
from shapely.geometry import box
from fiona.crs import from_epsg
import geopandas as gpd
from rasterio.mask import mask
import pycrs
import geojson
sys.path.append('config')
from connect import connect

# Argumentos
# parser = argparse.ArgumentParser()
# parser.add_argument("-s","--snap", nargs='*',help="Snap to pour point")
# parser.add_argument("-d","--delineate",nargs='*',help="Delineate catchment")
# args = vars(parser.parse_args())

# Variables de entorno
ruta = os.environ["PATH_FILES"]

# Generar bbox
def generateCoordinates(c,rad,tipo):
	result = 0
	if(tipo == 'lon'):
		result = float(rad)/110.54;
		print(result)
		return [c - result, c + result]
	elif(tipo == 'lat'):
		result = abs(float(rad)/(111.320*math.cos(c)))
		print(result)
		return [c - result, c + result]
   
# Convertir geometria a geojson
def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

# Cortar raster a partir de unas coordenada y un radio
def cutRaster(path,x,y,rad):
	data = rasterio.open(path)
	out_tif = os.path.join(ruta,"salidas","tmp","clipped.tiff")
	[minx, maxx] = generateCoordinates(x,rad,'lon')
	[miny, maxy] = generateCoordinates(y,rad,'lat')
	bbox = box(minx, miny, maxx, maxy)
	geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=from_epsg(4326))
	geo = geo.to_crs(crs=data.crs.data)
	coords = getFeatures(geo)
	out_img, out_transform = mask(dataset=data, shapes=coords, crop=True)
	out_meta = data.meta.copy()
	epsg_code = int(data.crs.data['init'][5:])
	out_meta.update({"driver": "GTiff",
		"height": out_img.shape[1],
		"width": out_img.shape[2],
		"transform": out_transform,
		"crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()})
	with rasterio.open(out_tif, "w", **out_meta) as dest:
		dest.write(out_img)
		return out_tif


# Obtener macroregion a partir de coordenada
def getRegionFromCoord(x,y):
	result = ''
	cursor = connect('postgresql_alfa').cursor()
	cursor.callproc('__wp_intersectmacroregionfromcoords',[x,y])
	result = cursor.fetchall()
	for row in result:
		result = row[0]
	cursor.close()
	return result
   
# Obtener ruta a partir de macroregion y parametro
def getPath(basin,parameter):
	result = ''
	cursor = connect('postgresql_alfa').cursor()
	cursor.callproc('__wp_getpathbasinparameter',[basin,parameter])
	result = cursor.fetchall()
	for row in result:
		result = row[0]
	cursor.close()
	return result
   
# Snap a red hidrica
def snap(path,x,y):
	grid = Grid.from_raster(path, data_name='acc')
	acc = grid.acc
	xy = [x,y]
	new_xy = grid.snap_to_mask(acc > 20, xy, return_dist=False)
	print(new_xy[0])
	print(new_xy[1])
	return [new_xy[0],new_xy[1]]
 
# Delimitar cuenca
def delineateCatchment(path,x,y):
	dirFlow = Grid.from_raster(path, data_name='dir')
	dirmap = (64,128,1,2, 4,8, 16,32)
	dirFlow.catchment(data='dir', x=x, y=y, dirmap=dirmap, out_name='catch',
               recursionlimit=15000, xytype='label')
	dirFlow.clip_to('catch')
	shapes = dirFlow.polygonize()
	schema = {
        'geometry': 'Polygon',
        'properties': {'LABEL': 'float:16'}
    }
	# with fiona.open('catchment.shp', 'w',
    #                 driver='ESRI Shapefile',
    #                 crs=dirFlow.crs.srs,
    #                 schema=schema) as c:
	# 	i = 0
	# 	for shape, value in shapes:
	# 		print(shape)
	# 		print(value)
	# 		rec = {}
	# 		rec['geometry'] = shape
	# 		rec['properties'] = {'LABEL' : str(value)}
	# 		rec['id'] = str(i)
	# 		c.write(rec)
	# 		i += 1
	for shape, value in shapes:
		polygon = geojson.Polygon(shape['coordinates'])
		features = []
		features.append(geojson.Feature(geometry=polygon,properties={"LABEL":str(value)}))
		feature_collection = geojson.FeatureCollection(features)
	return feature_collection
	

      
# Validacion de parametros
# if (args['snap']):
# 	x = float(args['snap'][0])
# 	y = float(args['snap'][1])
# 	basin = getRegionFromCoord(x,y)
# 	path = getPath(basin,2)
# 	path = cutRaster(path,x,y,5)
# 	[x,y] = snap(path,x,y)
# elif (args['delineate']):
# 	x = float(args['delineate'][0])
# 	y = float(args['delineate'][1])
# 	basin = getRegionFromCoord(x,y)
# 	path = getPath(basin,1)
# 	delineateCatchment(path,x,y)


