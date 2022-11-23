# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 10:30:33 2022

@author: lenovo
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

#%% read in production data 
irrigated = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\2010_I_prd.csv"
rainfed = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\2010_R_prd.csv"

df_i = pd.read_csv(irrigated, index_col = ['x', 'y'])
df_r = pd.read_csv(rainfed, index_col = ['x', 'y'])

#%% read in dryweight conversion and prices
value_df = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\gaez_dictionary_current_data.csv")
# for the columns that have a too large span of value -> NA 
value_df.dropna(inplace = True)
value_df['gaez_code'] = value_df['gaez_code'].str.lower()
value_dic = value_df.set_index('gaez_code').to_dict()['price']
conversion_dic = value_df.set_index('gaez_code').to_dict()['dw_conversion']

# some additional modifications as some differences in units between
# current and future yield
change_id = ['pls', 'cc2', 'fdd']
for i in change_id:
    value_dic[i] = 1 # 1 because already in prices
    
#%% get in right units
df_i = df_i * 1000
df_r = df_r * 1000
#%% prepare data 
current_list = [df_i, df_r]
names = ['v_2010_i', 'v_2010_r']
for counter,item in enumerate(current_list): 
    current_list[counter] = current_list[counter].drop(['band', 'spatial_ref', 'veg', 'nes', 'frt'], 
                                                       axis = 1)
    # multiplication with dryweight factor
    current_list[counter] = current_list[counter].mul(conversion_dic)
    current_list[counter] = current_list[counter].mul(value_dic)
    current_list[counter] = current_list[counter].sum(axis = 1)
    current_list[counter] = current_list[counter].reset_index().round({'x': 6, 'y':6})
    current_list[counter] = current_list[counter].rename(columns = {0: names[counter]})
    current_list[counter] = current_list[counter].set_index(['x', 'y'])
    
df_v = pd.concat(current_list, axis = 1)

#%% save data 
df_v.to_csv( r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\value_2010.csv")

#%% merge with other data 

df_v = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\value_2010.csv", index_col=['x', 'y'])

# then read in every other year for one rcp 

first_files = search_files(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data", "value_rcp2p6")

#first_files[1][72]
#first_files[0][65:69]

for counter, file in enumerate(first_files):
    df = pd.read_csv(file, index_col=['x', 'y'])
    """ df_v = df_v.join(pd.read_csv(file, 
                                 index_col=['x', 'y']).rename(columns = {'0': "value_" +file[65:69] + "_" + file[72]}),
                     how = "left")
    """
    if file[72] == 'I':
        df = df['0'].div(df_v['v_2010_i']).replace(np.inf, 0)
    elif file[72] == 'R':
        df = df['0'].div(df_v['v_2010_r']).replace(np.inf, 0)
    
    
    df =  df.to_frame().rename(columns = {0:  "value_" +file[65:69] + "_" + file[72]})
    
    df_v = df_v.join(df, how = 'left')#
    
#%% 
df_v.hist(column = 'v_2010_i', bins = 10000)


#%% test index -> this is not working -> but I don't know why
range_list =[[0.01, 0.1],[0.1, 0.2], [0.2, 0.3], [0.3, 0.4], [0.4, 0.5], [0.5, 0.6], [0.6, 0.7], 
 [0.7, 0.8], [0.8, 0.9], [0.9, 1], [1, 1.5], [1.5, 2], [2,3], [3, 5]]

value_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.5, 2, 3, 5]

for counter, item in enumerate(range_list):
    
    
    df_v['value_2080_R'] = np.where(df_v['value_2080_R'].between(item[0], 
                                                                 item[1]), 
                                    value_list[counter], df_v['value_2080_R'])    

#%% write back to tif
df_v.fillna(0, inplace = True)
df_v['value_2080_R'] = df['value_2080_R'].mask(df['value_2080_R'] > 2, 3)
df_v['value_2080_R'] = df['value_2080_R'].mask(df['value_2080_R'] < 0.1, 0)
df_v.dtypes
test = df_v.to_xarray()

test.value_2080_R.transpose('y', 'x').rio.to_raster(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\test_6.tif")
df_v['value_2080_R'].value_counts()
