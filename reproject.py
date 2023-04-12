from osgeo import gdal
import os

def reprojectRaster(inputFile, outputFile, outSrs):
    input_raster = gdal.Open(inputFile)
    gdal.Warp(outputFile,input_raster,dstSRS='EPSG:3857')



def reprojectMassive(inputFolder, outFolder, outSrs):
    for filename in os.listdir(inputFolder):
        if(filename.endswith(".tif")):
            base = os.path.basename(filename)
            fileNameWE = base.split(".")[0]
            labels = fileNameWE.split("_")
            outPath = os.path.join(outFolder,base)
            srcPath = os.path.join(inputFolder,filename)
            reprojectRaster(srcPath, outPath, outSrs)
            # resamplingRaster(templatePath,srcPath,outPath)
            # print(outPath)
            # print(srcPath)

def reprojectMassiveDirectories(inputFolder, outFolder, outSrs):
    listOfFile = os.listdir(inputFolder)
    completeFileList = list()
    for file in listOfFile:
        completePath = os.path.join(inputFolder, file)
        completePathOut = os.path.join(outFolder, file)
        if os.path.isdir(completePath):
            if not os.path.exists(completePathOut):
                os.mkdir(completePathOut)
            reprojectMassive(completePath, completePathOut, outSrs)
            completeFileList = completeFileList + getFiles(completePath)
        else:
            completeFileList.append(completePath)

        for item in completeFileList:
            print(item)

    return completeFileList

def getFiles(dirName):
    listOfFile = os.listdir(dirName)
    completeFileList = list()
    for file in listOfFile:
        completePath = os.path.join(dirName, file)
        if os.path.isdir(completePath):
            completeFileList = completeFileList + getFiles(completePath)
        else:
            completeFileList.append(completePath)

    return completeFileList

# fl = reprojectMassiveDirectories("/home/skaphe/Documentos/tnc/modelos/entradas/01-Precipitation/01-Historic/","/home/skaphe/Documentos/tnc/modelos/entradas/01-Precipitation3857/","EPSG:3857")
# print(fl)




reprojectMassive("/home/skaphe/Documentos/tnc/modelos/entradas/20-Soil_Index/","/home/skaphe/Documentos/tnc/modelos/entradas/20-Soil_Index3857/","EPSG:3857")






