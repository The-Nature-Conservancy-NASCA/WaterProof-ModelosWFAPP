import os, json, sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from entities import ParametroRuta
sys.path.append('config')
from config import config
from connect import connect
from sqlalchemy import func 


# Generar archivo de metadatos 
def generateMetadataFile(path,model, parameter,ext):
    metadataFilePath = os.path.join(path,'metadata.json')
    fileExists = os.path.isfile(metadataFilePath)
    metadataDict = {}

    if not fileExists:
        f = open(metadataFilePath,"w+")
        f.close()

    with open(metadataFilePath,'r+') as json_file:
        print(os.stat(metadataFilePath).st_size)
        
        if os.stat(metadataFilePath).st_size == 0:
            metadataDict = {"metadata": [{
                "model": model,
                "parameter": parameter,
                "ext": ext
            }]}
            json.dump(metadataDict, json_file)
        else:
            print("Existen datos")
            data = json.load(json_file)
            flag = False
            for p in data['metadata']:
                if (p["model"] == model and p["parameter"] == parameter and p["ext"] == ext):
                    flag = True
                    break

            if not flag:
                data['metadata'].append({"model":model,"parameter":parameter,"ext":ext})
            # json_file.truncate(0)
            json.dump(data, open(metadataFilePath,'r+'))


# Guardar rutas de parametros en la base de datos
def savePathParameter(paths,model):
    params = config(section='postgresql_alfa')
    connString = "postgresql://" + params['user'] + ":" + params['password'] + "@" + params['host'] + "/" + params['database']
    engine = create_engine(connString)
    Session = sessionmaker(bind=engine)
    session = Session()
    listParameters = getParametersByModel(model)
    for p in listParameters:
        id_parameter = p[0]
        nameParameter = p[1]
        cutType = p[2]
        constantType = p[3]
        suffixType = p[4]
        emptyType = p[5]
        fileType = p[6]
        folderType = p[7]
        outType = p[8]
        calcType = p[9]
        # inputType = p[10]
        # bioType = p[11]
        # preprocType = p[12]
        # riosType = p[13]
        # print(suffixType)


        if folderType:
            for path in paths:
                metadataPath = os.path.join(path,"metadata.json")
                with open(metadataPath,'r') as json_file:
                    data = json.load(json_file)
                    for item in data["metadata"]:
                        modelI = item["model"]
                        extI = item["ext"]
                        parameterI = item["parameter"]
                        if modelI == model and parameterI == nameParameter and extI == "folder":
                            for filename in os.listdir(path):
                                if "_" in filename:
                                    label_basin = filename
                                    id_basin = BasinByLabel(label_basin)[0]
                                    ruta = os.path.join(path,filename)
                                    q = session.query(ParametroRuta).filter(ParametroRuta.id_basin == id_basin,ParametroRuta.id_parametro == id_parameter).count()
                                    maxid = session.query(func.max(ParametroRuta.id_parametro_ruta)).scalar()
                                    if q == 0:
                                        newPR = ParametroRuta(id_parametro_ruta=maxid+1,id_basin=id_basin,ruta=ruta,id_parametro=id_parameter)
                                        session.add(newPR)
                                    else:
                                        UPR = session.query(ParametroRuta).filter(ParametroRuta.id_basin == id_basin,ParametroRuta.id_parametro == id_parameter).first() 
                                        UPR.ruta = ruta

                                    session.commit()

        elif constantType or suffixType or emptyType or fileType or outType:
            listBasins = getAllBasins()
            for b in listBasins:
                id_basin = b[0]
                ruta = ""
                q = session.query(ParametroRuta).filter(ParametroRuta.id_basin == id_basin,ParametroRuta.id_parametro == id_parameter).count()
                maxid = session.query(func.max(ParametroRuta.id_parametro_ruta)).scalar()
                if q == 0:
                    newPR = ParametroRuta(id_parametro_ruta=maxid+1,id_basin=id_basin,ruta=ruta,id_parametro=id_parameter)
                    session.add(newPR)
                else:
                    UPR = session.query(ParametroRuta).filter(ParametroRuta.id_basin == id_basin,ParametroRuta.id_parametro == id_parameter).first() 
                    UPR.ruta = ruta

                session.commit()
        elif cutType != None:
            for path in paths:
                metadataPath = os.path.join(path,"metadata.json")
                with open(metadataPath,'r') as json_file:
                    data = json.load(json_file)
                    for item in data["metadata"]:
                        modelI = item["model"]
                        extI = item["ext"]
                        parameterI = item["parameter"]
                        if modelI == model and parameterI == nameParameter:
                            for filename in os.listdir(path):
                                if filename.endswith(extI):                                    
                                    ruta = os.path.join(path,filename)
                                    basename = filename.split(".")[0]
                                    parts = basename.split("_")
                                    if "YEAR" in basename:
                                        label_basin = parts[1] + "_" + parts[2]
                                    else:
                                        label_basin = parts[-2] + "_" + parts[-1]
                                    id_basin = BasinByLabel(label_basin)[0]
                                    q = session.query(ParametroRuta).filter(ParametroRuta.id_basin == id_basin,ParametroRuta.id_parametro == id_parameter).count()
                                    maxid = session.query(func.max(ParametroRuta.id_parametro_ruta)).scalar()
                                    if q == 0:
                                        newPR = ParametroRuta(id_parametro_ruta=maxid+1,id_basin=id_basin,ruta=ruta,id_parametro=id_parameter)
                                        session.add(newPR)
                                    else:
                                        UPR = session.query(ParametroRuta).filter(ParametroRuta.id_basin == id_basin,ParametroRuta.id_parametro == id_parameter).first() 
                                        UPR.ruta = ruta

                                    session.commit()
        elif cutType is None:
            if id_parameter == 5 or id_parameter == 22 or id_parameter == 27 or id_parameter == 28 or id_parameter == 43 or id_parameter == 45 or id_parameter == 46 or id_parameter==78:
                ruta = "False"
            elif id_parameter == 36 or id_parameter == 37:
                ruta = "True"
            listBasins = getAllBasins()
            for b in listBasins:
                id_basin = b[0]
                q = session.query(ParametroRuta).filter(ParametroRuta.id_basin == id_basin,ParametroRuta.id_parametro == id_parameter).count()
                maxid = session.query(func.max(ParametroRuta.id_parametro_ruta)).scalar()
                if q == 0:
                    newPR = ParametroRuta(id_parametro_ruta=maxid+1,id_basin=id_basin,ruta=ruta,id_parametro=id_parameter)
                    session.add(newPR)
                else:
                    UPR = session.query(ParametroRuta).filter(ParametroRuta.id_basin == id_basin,ParametroRuta.id_parametro == id_parameter).first() 
                    UPR.ruta = ruta

                session.commit()







            
                


# Recuperar parametros por modelo
def getParametersByModel(model):
    results = []
    cursor = connect('postgresql_alfa').cursor()
    cursor.callproc('__wp_getparametersbymodel',[model])
    result = cursor.fetchall()
    for row in result:
        results.append(row)
    cursor.close()
    return results


# Recuperar parametro por nombre
def getParameter(name):
	result = ''
	cursor = connect('postgresql').cursor()
	cursor.callproc('__wp_getparameterbyname',[name])
	result = cursor.fetchall()
	for row in result:
		result = row
	cursor.close()
	return result

# Recuperar todas las macroregiones
def getAllBasins():
    results = []
    cursor = connect('postgresql').cursor()
    cursor.callproc('__wp_getallbasins',[])
    result = cursor.fetchall()
    for row in result:
        results.append(row)
    cursor.close()
    return results

# Recuperar macroregion a partir de label
def BasinByLabel(label):
    results = ""
    cursor = connect('postgresql').cursor()
    cursor.callproc('__wp_getbasinbylabel',[label])
    result = cursor.fetchall()
    for row in result:
        result = row
    cursor.close()
    return result

# awy
# generateMetadataFile("/data/global_datasets/21-Biophysical_Table/","awy","biophysical_table_path","csv")
# generateMetadataFile("/data/global_datasets/08-Soil_Depth/","awy","depth_to_root_rest_layer_path","tif")
# generateMetadataFile("/data/global_datasets/02-Evapotranspiration/01-Historic/YEAR/","awy","eto_path","tif")
# generateMetadataFile("/data/global_datasets/03-LandCover/YEAR_0/","awy","lulc_path","tif")
# generateMetadataFile("/data/global_datasets/09-Plant_Available_Water/","awy","pawc_path","tif")
# generateMetadataFile("/data/global_datasets/01-Precipitation/01-Historic/YEAR/","awy","precipitation_path","tif")

# # # swy
# generateMetadataFile("/data/global_datasets/21-Biophysical_Table/","swy","biophysical_table_path","csv")
# generateMetadataFile("/data/global_datasets/10-DEM/","swy","dem_raster_path","tif")
# generateMetadataFile("/data/global_datasets/02-Evapotranspiration/01-Historic/","swy","et0_dir","folder")
# generateMetadataFile("/data/global_datasets/03-LandCover/YEAR_0/","swy","lulc_raster_path","tif")
# generateMetadataFile("/data/global_datasets/01-Precipitation/01-Historic/","swy","precip_dir","folder")
# generateMetadataFile("/data/global_datasets/14-Day_Rainfall/","swy","rain_events_table_path","folder")
# generateMetadataFile("/data/global_datasets/04-SoilGroup/","swy","soil_group_path","tif")

# # # ndr
# generateMetadataFile("/data/global_datasets/21-Biophysical_Table/","ndr","biophysical_table_path","csv")
# generateMetadataFile("/data/global_datasets/10-DEM/","ndr","dem_path","tif")
# generateMetadataFile("/data/global_datasets/03-LandCover/YEAR_0/","ndr","lulc_path","tif")
# generateMetadataFile("/data/global_datasets/01-Precipitation/01-Historic/YEAR/","ndr","runoff_proxy_path","tif")

# # # sdr
# generateMetadataFile("/data/global_datasets/21-Biophysical_Table/","sdr","biophysical_table_path","csv")
# generateMetadataFile("/data/global_datasets/10-DEM/","sdr","dem_path","tif")
# generateMetadataFile("/data/global_datasets/03-LandCover/YEAR_0/","sdr","lulc_path","tif")
# generateMetadataFile("/data/global_datasets/07-Soil_Erodability/","sdr","erodibility_path","tif")
# generateMetadataFile("/data/global_datasets/06-Rainfall_Erosivity/01-Historic/","sdr","erosivity_path","tif")

# # # carbon
# generateMetadataFile("/data/global_datasets/21-Biophysical_Table/","carbon","carbon_pools_path","csv")
# generateMetadataFile("/data/global_datasets/03-LandCover/YEAR_0/","carbon","lulc_cur_path","tif")

# #preprocRIOS
# generateMetadataFile("/data/global_datasets/03-LandCoverResampling/","preprocRIOS","lulc_raster_uri","tif")
# generateMetadataFile("/data/global_datasets/21-Biophysical_Table/","preprocRIOS","rios_coeff_table","csv")
# generateMetadataFile("/data/global_datasets/10-DEM/","preprocRIOS","dem_raster_uri","tif")
# generateMetadataFile("/data/global_datasets/20-Soil_IndexResampling/","preprocRIOS","soil_texture_raster_uri","tif")
# generateMetadataFile("/data/global_datasets/01-PrecipitationResampling/","preprocRIOS","precip_annual_raster_uri","tif")
# generateMetadataFile("/data/global_datasets/06-Rainfall_ErosivityResampling/","preprocRIOS","erosivity_raster_uri","tif")
# generateMetadataFile("/data/global_datasets/07-Soil_ErodabilityResampling/","preprocRIOS","erodibility_raster_uri","tif")
# generateMetadataFile("/data/global_datasets/08-Soil_DepthResampling/","preprocRIOS","soil_depth_raster_uri","tif")
# generateMetadataFile("/data/global_datasets/02-EvapotranspirationResampling/","preprocRIOS","aet_raster_uri","tif")
# generateMetadataFile("/data/global_datasets/30-Stream/","preprocRIOS","streams_raster_uri","tif")
generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/01-Precipitation/01-Historic/","preprocRIOS","precip_month_raster_uri","folder")

# # # RIOS
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/03-LandCover/YEAR_0/","rios","lulc_uri","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/08-Soil_Depth/","rios","Soil depth","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/07-Soil_Erodability/","rios","Soil erodibility","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/19-Beneficiaries/","rios","Beneficiaries","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/06-Rainfall_Erosivity/01-Historic/","rios","Rainfall erosivity","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/20-Soil_Index/","rios","Soil Texture Index","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/06-Rainfall_Erosivity/01-Historic/","rios","Rainfall depth","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/18-Recharge_Area/","rios","Preferential Recharge Areas","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/02-Evapotranspiration/01-Historic/YEAR/","rios","Actual Evapotranspiration","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/01-Precipitation/01-Historic/YEAR/","rios","Annual Average Rainfall","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/21-Biophysical_Table/","rios","lulc_coefficients_table_uri","csv")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/21-Biophysical_Table/","rios","On-pixel retention","csv")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/21-Biophysical_Table/","rios","On-pixel source","csv")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/21-Biophysical_Table/","rios","Vegetative Cover Index","csv")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/21-Biophysical_Table/","rios","Land Use Land Cover Retention at pixel","csv")


# # # awy
# savePathParameter(["/data/global_datasets/21-Biophysical_Table/",
# "/data/global_datasets/08-Soil_Depth/",
# "/data/global_datasets/03-LandCover/YEAR_0/",
# "/data/global_datasets/09-Plant_Available_Water/",
# "/data/global_datasets/02-Evapotranspiration/01-Historic/YEAR/",
# "/data/global_datasets/01-Precipitation/01-Historic/YEAR/"],'awy')

# # # swy
# savePathParameter(["/data/global_datasets/21-Biophysical_Table/",
# "/data/global_datasets/10-DEM/",
# "/data/global_datasets/02-Evapotranspiration/01-Historic/",
# "/data/global_datasets/03-LandCover/YEAR_0/",
# "/data/global_datasets/01-Precipitation/01-Historic/",
# "/data/global_datasets/14-Day_Rainfall/",
# "/data/global_datasets/04-SoilGroup/"],'swy')

# # sdr
# savePathParameter(["/data/global_datasets/21-Biophysical_Table/",
# "/data/global_datasets/03-LandCover/YEAR_0/",
# "/data/global_datasets/10-DEM/",
# "/data/global_datasets/07-Soil_Erodability/",
# "/data/global_datasets/06-Rainfall_Erosivity/01-Historic/"],'sdr')

# # ndr
# savePathParameter(["/data/global_datasets/21-Biophysical_Table/",
# "/data/global_datasets/03-LandCover/YEAR_0/",
# "/data/global_datasets/10-DEM/",
# "/data/global_datasets/01-Precipitation/01-Historic/YEAR/"],'ndr')

# # carbon
# savePathParameter(["/data/global_datasets/21-Biophysical_Table/",
# "/data/global_datasets/03-LandCover/YEAR_0/"],'carbon')

# # # preprocRIOS
# savePathParameter(["/data/global_datasets/03-LandCoverResampling/",
# "/data/global_datasets/21-Biophysical_Table/",
# "/data/global_datasets/10-DEM/",
# "/data/global_datasets/20-Soil_IndexResampling/",
# "/data/global_datasets/01-PrecipitationResampling/",
# "/data/global_datasets/06-Rainfall_ErosivityResampling/",
# "/data/global_datasets/07-Soil_ErodabilityResampling/",
# "/data/global_datasets/08-Soil_DepthResampling/",
# "/data/global_datasets/02-EvapotranspirationResampling/",
# "/data/global_datasets/30-Stream/",
# "/data/global_datasets/14-Day_RainfallResampling/"],'preprocRIOS')


# # # RIOS
savePathParameter(["/home/skaphe/Documentos/tnc/modelos/entradas/03-LandCover/YEAR_0/",
"/home/skaphe/Documentos/tnc/modelos/entradas/08-Soil_Depth/",
"/home/skaphe/Documentos/tnc/modelos/entradas/07-Soil_Erodability/",
"/home/skaphe/Documentos/tnc/modelos/entradas/19-Beneficiaries/",
"/home/skaphe/Documentos/tnc/modelos/entradas/06-Rainfall_Erosivity/01-Historic/",
"/home/skaphe/Documentos/tnc/modelos/entradas/18-Recharge_Area/",
"/home/skaphe/Documentos/tnc/modelos/entradas/02-Evapotranspiration/01-Historic/YEAR/",
"/home/skaphe/Documentos/tnc/modelos/entradas/01-Precipitation/01-Historic/YEAR/",
"/home/skaphe/Documentos/tnc/modelos/entradas/21-Biophysical_Table/",
"/home/skaphe/Documentos/tnc/modelos/entradas/20-Soil_Index/"],'rios')


# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/03-LandCover/YEAR_0/","rios","lulc_uri","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/08-Soil_Depth/","rios","Soil depth","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/07-Soil_Erodability/","rios","Soil erodibility","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/19-Beneficiaries/","rios","Beneficiaries","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/06-Rainfall_Erosivity/01-Historic/","rios","Rainfall erosivity","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/20-Soil_Index/","rios","Soil Texture Index","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/06-Rainfall_Erosivity/01-Historic/","rios","Rainfall depth","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/18-Recharge_Area/","rios","Preferential Recharge Areas","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/02-Evapotranspiration/01-Historic/YEAR/","rios","Actual Evapotranspiration","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/01-Precipitation/01-Historic/YEAR/","rios","Annual Average Rainfall","tif")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/21-Biophysical_Table/","rios","lulc_coefficients_table_uri","csv")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/21-Biophysical_Table/","rios","On-pixel retention","csv")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/21-Biophysical_Table/","rios","On-pixel source","csv")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/21-Biophysical_Table/","rios","Vegetative Cover Index","csv")
# generateMetadataFile("/home/skaphe/Documentos/tnc/modelos/entradas/21-Biophysical_Table/","rios","Land Use Land Cover Retention at pixel","csv")










        


        

