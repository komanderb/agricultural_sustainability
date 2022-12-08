# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 10:03:56 2022

@author: Bjoern Komander

File for processing gridded GDP data 
"""
import rasterio
import geopandas as gpd
import pandas as pd
import numpy as np
import scipy.io
from osgeo import gdal 
import rioxarray
import os
import re

# set os.chdir to import functions from utils
os.chdir(r"C:\Users\lenovo\Documents\GitHub\agricultural_sustainability\code")

from utils import search_files

#%% read in data

file_gdp = r"G:\Meine Ablage\agricultural_sustain\gdp\gridded_gdp\GDP2005_1km.tif"

# choose some tif just for reference 
file_current = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\current_yields\alfa200a_yld.tif"
#%% open tifs with gdal

g_gdp = gdal.Open(file_gdp)
g_curr = gdal.Open(file_current)


#%% gdal warp 
# out path
out_tif = r"G:\Meine Ablage\agricultural_sustain\gdp\gridded_gdp\GDP2005.tif"

# define dest spatial reference
dest_ref = g_curr.GetSpatialRef()
dest_width = g_curr.RasterXSize
dest_height = g_curr.RasterYSize

# define bounds (to align with grid)
bounds = [-180.0, -90.0, 180.0, 90.0]


kwargs = {'resampleAlg': 'sum', 'dstSRS': dest_ref,
          'width': dest_width, 'height': dest_height,
          'outputBounds': bounds}
gdal.Warp(out_tif, file_gdp, **kwargs)

#%% check output
file_final = r"G:\Meine Ablage\agricultural_sustain\gdp\gridded_gdp\GDP2005.tif"
gdp_test = gdal.Open(file_final)

print(gdp_test.RasterXSize, g_curr.RasterXSize)
del(gdp_test)




#%% same population with population
out_tif = r"G:\Meine Ablage\agricultural_sustain\population\population_2005.tif"
file_pop = r"G:\Meine Ablage\agricultural_sustain\population\gpw_v4_population_count_rev11_2005_30_sec.tif"
# check crs of population file
pop = gdal.Open(file_pop)
pop.GetProjection()
# update no data value -> different to gdp

kwargs = {'resampleAlg': 'sum', 'dstSRS': dest_ref,
          'width': dest_width, 'height': dest_height,
          'outputBounds': bounds, 'srcNodata': -3.4028230607370965e+38,
          'dstNodata': 0} # 0 maybe a bit strong ey -> but only summarising
gdal.Warp(out_tif, file_pop, **kwargs)


