import gdal, gdalconst, os

def getUnitsPerPixel(rasterPath):
    raster = gdal.Open(rasterPath)
    gt =raster.GetGeoTransform()
    pixelSizeX = gt[1]
    pixelSizeY =-gt[5]
    print("size X: {0}".format(str(pixelSizeX)))
    print("size Y: {0}".format(str(pixelSizeY)))




def resamplingRaster(templatePath,srcPath,out):

    # Source
    src = gdal.Open(srcPath, gdalconst.GA_ReadOnly)
    src_proj = src.GetProjection()
    src_geotrans = src.GetGeoTransform()

    print(templatePath)
    # We want a section of source that matches this:
    match_ds = gdal.Open(templatePath, gdalconst.GA_ReadOnly)
    match_proj = match_ds.GetProjection()
    match_geotrans = match_ds.GetGeoTransform()
    wide = match_ds.RasterXSize
    high = match_ds.RasterYSize

    # Output / destination
    dst = gdal.GetDriverByName('Gtiff').Create(out, wide, high, 1, gdalconst.GDT_Float32)
    dst.SetGeoTransform( match_geotrans )
    dst.SetProjection( match_proj)

    # Do the work
    gdal.ReprojectImage(src, dst, src_proj, match_proj, gdalconst.GRA_Bilinear)

    del dst # Flush

    print ("finish")

# resamplingRaster("/home/skaphe/Documentos/tnc/modelos/entradas/10-DEM/DEM_AF_1.tif","/home/skaphe/Documentos/tnc/modelos/entradas/03-LandCover/YEAR_0/LULC_AF_1.tif","resamplig.tif")

def batchProcess(srcFolder, templateFolder, outFolder):
    for filename in os.listdir(srcFolder):
        if(filename.endswith(".tif")):
            base = os.path.basename(filename)
            fileNameWE = base.split(".")[0]
            labels = fileNameWE.split("_")
            print(labels)
            templatePath = os.path.join(templateFolder,"DEM_" + labels[1] + "_" + labels[2] + ".tif")
            outPath = os.path.join(outFolder,base)
            srcPath = os.path.join(srcFolder,filename)
            resamplingRaster(templatePath,srcPath,outPath)
            print(base)
            # print(templatePath)
            # print(outPath)

batchProcess("/home/skaphe/Documentos/tnc/modelos/entradas/01-Precipitation/01-Historic/SI_6/","/home/skaphe/Documentos/tnc/modelos/entradas/10-DEM/","/home/skaphe/Documentos/tnc/modelos/entradas/01-PrecipitationResampling/01-Historic/SI_6/")




