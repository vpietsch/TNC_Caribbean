#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      vpmcnulty
#
# Created:     24/08/2020
# Copyright:   (c) vpmcnulty 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy

#Input variables for tool
workspace = arcpy.GetParameterAsText(0) #scratch workspace for intermediate products. Must be a geodatabase.
mpas = arcpy.GetParameterAsText(1) #MPA layer
zone = arcpy.GetParameterAsText(2) #Could be nearshore environment, EEZ, other. Must have a country field. CCI/EEZs should be updated every 2 years
zonedescriptor = arcpy.GetParameterAsText(3) #CCI or EEZ, etc.
desgn = arcpy.GetParameterAsText(4) #Specify designated or proposed
country_field = arcpy.GetParameterAsText(5) #Of zone file (Moot_cci is Government, EEZ is DISSOLVE, etc.)
outputfolder = arcpy.GetParameterAsText(6)

arcpy.env.overwriteOutput = True

#Calculate area of each country's zone
zone1 = workspace+'/zones'
arcpy.CopyFeatures_management(zone,zone1)
arcpy.AddField_management(zone1,"area_sqkm_zone","DOUBLE")
##arcpy.CalculateField_management(zone,"area_sqkm_zone","!shape.area@squarekilometers!","PYTHON_9.3","#")
arcpy.AddGeometryAttributes_management(zone1, "AREA", "", "SQUARE_KILOMETERS", "PROJCS['WGS_1984_Lambert_Azimuthal_Equal_Area',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Azimuthal_Equal_Area'],PARAMETER['false_easting',0.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-76.0],PARAMETER['latitude_of_origin',16.0],UNIT['Meters',1.0]]")
arcpy.CalculateField_management(zone1,"area_sqkm_zone","!POLY_AREA!","PYTHON_9.3")
print('zone area calculated')

#Select Designated or Proposed Areas
mpas_lyr = arcpy.MakeFeatureLayer_management(mpas)
arcpy.SelectLayerByAttribute_management(mpas_lyr,"NEW_SELECTION","STATUS = '"+desgn+"'")
print('MMAs selected')

#Dissolve MPA layer to eliminate double-counting area of overlapping MMAs
mpas_dissolve = workspace+"/MPAs_"+desgn+"_Dissolve"
arcpy.Dissolve_management(mpas_lyr, mpas_dissolve, dissolve_field="")
print('MMAs dissolved')

#Intersect MPA layer with zone layer]
intlayer = workspace+"/intersect"
intfeatures = [mpas_dissolve, zone1]
arcpy.Intersect_analysis(intfeatures, intlayer, "ALL")
print('MMAs and zones intersected')

#Summarize by Country using (Government) field from zone layer - user should specify the country name field
intlayer_dissolve = workspace+"/intersect_dissolvebycountry"
arcpy.Dissolve_management(intlayer, intlayer_dissolve, dissolve_field=country_field)
print('intersected layer dissolved by country')

#Calculate area of dissolved intersected file
arcpy.AddField_management(intlayer_dissolve,"area_sqkm_mmas","DOUBLE")
##arcpy.CalculateField_management(intlayer_dissolve,"area_sqkm_mmas","!shape.area@squarekilometers!","PYTHON_9.3","#")
arcpy.AddGeometryAttributes_management(intlayer_dissolve, "AREA", "", "SQUARE_KILOMETERS", "PROJCS['WGS_1984_Lambert_Azimuthal_Equal_Area',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Azimuthal_Equal_Area'],PARAMETER['false_easting',0.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-76.0],PARAMETER['latitude_of_origin',16.0],UNIT['Meters',1.0]]")
arcpy.CalculateField_management(intlayer_dissolve,"area_sqkm_mmas","!POLY_AREA!","PYTHON_9.3")
print('MMA area calculated by country')

#Calculate Percentages
zone_FL = arcpy.MakeFeatureLayer_management(zone1)
intlayer_dissolve_FL = arcpy.MakeFeatureLayer_management(intlayer_dissolve)
joined_table = arcpy.AddJoin_management(zone_FL,country_field,intlayer_dissolve_FL,country_field)
print('intersected dissolved layer joined to zone layer')

finalzones = workspace+'/final_zone_layer'
arcpy.CopyFeatures_management(joined_table, finalzones)
arcpy.AddField_management(finalzones,"Percent","DOUBLE")
arcpy.CalculateField_management(finalzones,"Percent","(!intersect_dissolvebycountry_area_sqkm_mmas!/!zones_area_sqkm_zone!)*100","PYTHON_9.3")
print('percentages calculated')

#Export to a TXT
arcpy.TableToTable_conversion(finalzones,outputfolder,'MMA_Percents_'+zonedescriptor+'.txt')
print('text file created')
