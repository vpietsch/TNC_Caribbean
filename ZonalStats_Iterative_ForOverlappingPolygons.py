#-------------------------------------------------------------------------------
# Name:        Zonal Statistics as Table - Iterative, for Overlapping Polygons
# Purpose:
#
# Author:      vpmcnulty
#
# Created:     03/01/2020
# Copyright:   (c) vpmcnulty 2020
# Licence:     <your licence>

import arcpy, os, sys, string
from arcpy import env
arcpy.CheckOutExtension("spatial")
def CreateDirectory(DBF_dir):
    if not os.path.exists(DBF_dir):
        os.mkdir(DBF_dir)
        print "created directory {0}".format(DBF_dir)

def ZonalStasAsTable(fc,DBF_dir,raster,zoneField):
    for row in arcpy.SearchCursor(fc):
        lyr = "Zone_{0}_lyr".format(row.OBJECTID)
        tempTable = DBF_dir + os.sep + "zone_{0}.dbf".format(row.OBJECTID)
        arcpy.MakeFeatureLayer_management(fc, lyr, "\"OBJECTID\" = {0}".format(row.OBJECTID))
        print "Creating layer {0}".format(lyr)
        out_layer = DBF_dir + os.sep + lyr + ".lyr"
        arcpy.SaveToLayerFile_management(lyr, out_layer, "ABSOLUTE")
        print "Saved layer file"
        arcpy.gp.ZonalStatisticsAsTable_sa(out_layer, zoneField, raster, tempTable, "DATA", "ALL")
        print "Populating zonal stats for {0}".format(lyr)
    del row, lyr

def MergeTables(DBF_dir,zstat_table):
    arcpy.env.workspace = DBF_dir
    tableList = arcpy.ListTables()
    arcpy.Merge_management(tableList,zstat_table)
    print "Merged tables. Final zonalstat table {0} created. Located at {1}".format(zstat_table,DBF_dir)
    del tableList
if __name__ == "__main__":
    ws = "C:/TEMP"
    DBF_dir = ws + os.sep + "DBFile"
    fc = "C:/TEMP/zone/zone_data/zones.gdb/All1kmPoints_InVEST_5kmBuffer_Countries"
    raster = r"C:/TEMP/zone/raster/car_clm_hurricanes.img"
    zoneField = "ID_Final"
    zstat_table = DBF_dir + os.sep + "Zonalstat.dbf"
    CreateDirectory(DBF_dir)
    ZonalStasAsTable(fc,DBF_dir,raster,zoneField)
    MergeTables(DBF_dir,zstat_table)