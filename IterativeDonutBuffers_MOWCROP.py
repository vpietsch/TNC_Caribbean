#-------------------------------------------------------------------------------
# Name:        Donut Buffer Rings
# Purpose:
#
# Author:      vpmcnulty
#
# Created:     07/10/2020
# Copyright:   (c) vpmcnulty 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy
workspace = "C:/Caribbean/6_Projects/2019_2021_MOW_CROP/2020_04_RecFishing/RecFishing_12102020.gdb"
arcpy.env.workspace = workspace
PAMs = "C:/Caribbean/6_Projects/2019_2021_MOW_CROP/2020_04_RecFishing/RecFishing_12102020.gdb/OnshoreRecFish_10Dec20_ALL"
arcpy.env.overwriteOutput = True


arcpy.MakeFeatureLayer_management(PAMs,"PAMs_lyr")
with arcpy.da.SearchCursor(PAMs,['OBJECTID_1']) as cursor:
    for row in cursor:
        objid = row[0]
        print('Selecting '+str(objid))
        expression = "OBJECTID_1 = "+str(objid)
        print(expression)
        arcpy.management.SelectLayerByAttribute("PAMs_lyr", "NEW_SELECTION", expression)
        arcpy.analysis.Buffer("PAMs_lyr", workspace+"/BUFFER_10km_ID"+str(objid), "10 Kilometers", "FULL", "ROUND", "NONE", None, "PLANAR")
        arcpy.analysis.Buffer("PAMs_lyr", workspace+"/BUFFER_20km_ID"+str(objid), "20 Kilometers", "FULL", "ROUND", "NONE", None, "PLANAR")
        arcpy.analysis.Buffer("PAMs_lyr", workspace+"/BUFFER_40km_ID"+str(objid), "40 Kilometers", "FULL", "ROUND", "NONE", None, "PLANAR")
        arcpy.analysis.Erase(workspace+"/BUFFER_20km_ID"+str(objid), workspace+"/BUFFER_10km_ID"+str(objid), workspace+"/DONUT_20km_ID"+str(objid), None)
        arcpy.analysis.Erase(workspace+"/BUFFER_40km_ID"+str(objid), workspace+"/BUFFER_20km_ID"+str(objid), workspace+"/DONUT_40km_ID"+str(objid), None)

