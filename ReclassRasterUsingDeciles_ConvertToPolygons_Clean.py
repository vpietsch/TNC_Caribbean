#-------------------------------------------------------------------------------
# Name:        Reclassify raster using deciles & convert to polygons
# Purpose:
#
# Author:      vpmcnulty
#
# Created:     19/11/2020
# Copyright:   (c) vpmcnulty 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import arcpy
import numpy as np
from osgeo import gdal, gdal_array
import glob
import subprocess
import os
arcpy.env.overwriteOutput = True

#Step 1: Convert feature rasters to GeoTIFFs
# open the dataset and retrieve raster data as an array
workspace = r"C:\Caribbean\6_Projects\2019_2021_MOW_CROP\2020_10_ReportMaps\NDB_Model_Outputs_20201119.gdb"
arcpy.env.workspace = workspace
fcs = arcpy.ListRasters()
print(fcs)

for fc in fcs:
    print(fc)
    arcpy.CopyRaster_management(fc,"C:/Caribbean/6_Projects/2019_2021_MOW_CROP/2020_10_ReportMaps/NDB_ModelOutputs_20201119_GeoTIFFs/"+fc+".tif")


#Step 2: Reclassify using 10 quantiles
workspace = r"C:\Caribbean\6_Projects\2019_2021_MOW_CROP\2020_10_ReportMaps\NDB_ModelOutputs_20201119_GeoTIFFs"
arcpy.env.workspace = workspace
fcs2 = arcpy.ListRasters()

for fc in fcs2:
    print(fc)
    fcname = 'C:/Caribbean/6_Projects/2019_2021_MOW_CROP/2020_10_ReportMaps/NDB_ModelOutputs_20201119_GeoTIFFs/'+fc
    dataset = gdal.Open(fcname)
    rasterArray = arcpy.RasterToNumPyArray(fcname)
    nodata = rasterArray.max()
    remove = np.array(nodata)
    array_calcquant = np.setdiff1d(rasterArray,remove)

    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    nodata_val = band.GetNoDataValue()
    if nodata_val is not None:
        array = np.ma.masked_equal(array, nodata_val)

    array_ignored_nan = array[array >= array.min()]

    # create an array of zeros the same shape as the input array
    output = np.zeros_like(array).astype(np.uint8)

    maximum = np.quantile(array_calcquant,1)
    percentile_90 = np.quantile(array_calcquant,0.9)
    percentile_80 = np.quantile(array_calcquant,0.8)
    percentile_70 = np.quantile(array_calcquant,0.7)
    percentile_60 = np.quantile(array_calcquant,0.6)
    percentile_50 = np.quantile(array_calcquant,0.5)
    percentile_40 = np.quantile(array_calcquant,0.4)
    percentile_30 = np.quantile(array_calcquant,0.3)
    percentile_20 = np.quantile(array_calcquant,0.2)
    percentile_10 = np.quantile(array_calcquant,0.1)
    percentile_0 = np.quantile(array_calcquant,0)

    print(fc, percentile_0, percentile_10, percentile_20, percentile_30, percentile_40, percentile_50, percentile_60, percentile_70, percentile_80, percentile_90, maximum)

    output = np.where((array > percentile_0), 1, output)
    output = np.where((array > percentile_10), 2, output)
    output = np.where((array > percentile_20), 3, output)
    output = np.where((array > percentile_30), 4, output)
    output = np.where((array > percentile_40), 5, output)
    output = np.where((array > percentile_50), 6, output)
    output = np.where((array > percentile_60), 7, output)
    output = np.where((array > percentile_70), 8, output)
    output = np.where((array > percentile_80), 9, output)
    output = np.where((array > percentile_90), 10, output)
    output = np.where((array > maximum), 99999999, output)

    outname = "C:/Caribbean/6_Projects/2019_2021_MOW_CROP/2020_10_ReportMaps/NDB_ModelOutputs_20201119_GeoTIFFs_Reclassified/"+fc
    gdal_array.SaveArray(output, outname, "gtiff", prototype=dataset)

    #Step 3: Convert rasters to polygons
    arcpy.RasterToPolygon_conversion(outname,"C:/Caribbean/6_Projects/2019_2021_MOW_CROP/2020_10_ReportMaps/NDB_Model_Outputs_20201119_Reclassified_Polygons.gdb/"+fc[:-4]+"_poly","NO_SIMPLIFY")




