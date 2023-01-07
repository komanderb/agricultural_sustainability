# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 09:52:28 2022

@author: Bjoern Komander

File to make unified database out of the different tifs
We only realised after a while that current production and future yields 
do not measure the same thing. Therefore only the last function is used to create 
the data we use now, limited to future yields. 
"""

#%% import relevant libraries

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

#%% start the process

# we start with total production for 2010
in_dir = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\res06\T\2010"

expr = "prd.tif$"

list_of_files = search_files(in_dir, expr)

#%% make regex for variable names
# that also can be smarter (and faster within the function)
column_names = []
for file in list_of_files:
    column_names.append(file[60:63])
    
    
#%% function to merge data

def gaez_merger(in_dir, water_type, gaez_type, out_dir):
    """
    

    Parameters
    ----------
    in_dir : TYPE
        DESCRIPTION.
    water_type : TYPE
        DESCRIPTION.
    gaez_type : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    
    if gaez_type == "prd":
        expr = "prd.tif$"
        
    elif gaez_type == "har":
        expr = "har.tif$"
    
    elif gaez_type == "yld":
        expr = "yld.tif$"
        
    else:
        raise ValueError("gaez_type must be one of prd, har, yld")
    
    list_of_files = search_files(in_dir, expr)
    
    for counter, file in enumerate(list_of_files):
        if counter < 1: 
            # open tifs into as array for each pixel
            rds = rioxarray.open_rasterio(file)
            # translate that to dataframe, name the value column according 
            df = rds.to_dataframe(file[60:63])
            
        else:
            rds = rioxarray.open_rasterio(file)
            # left_join here 
            df = df.join(rds.to_dataframe(file[60:63]), how = "left", rsuffix="DROP").filter(regex="^(?!.*DROP)")
            
    df.to_csv(out_dir + "/2010" + "_" + water_type + "_" + gaez_type + ".csv")
    #return df


#%% big loop 

gaez_types = ["prd", "har"] # leave out yield for now

water_types = ["R", "I", "T"]

directories = [r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\res06\R\2010",
               r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\res06\I\2010",
               r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\res06\T\2010"]


out = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data"

for counter, item in enumerate(water_types):
    for g_type in gaez_types:
        gaez_merger(directories[counter], item, g_type, out)


#%% process future yield data 

def merger_future(out_dir, crop_dict, crop_value):
    """
    

    Parameters
    ----------
    out_dir : TYPE
        DESCRIPTION.
    crop_dict : TYPE
        DESCRIPTION.
    crop_value : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    base_dir = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\future_yields"
    
    rcp_list = ["rcp2p6", "rcp4p5", "rcp6p0", "rcp8p5"]
    time_list = ["2020sH", "2050sH", "2080sH"]
    water_supply = ["irrigated", "rainfed"]
    # read in harvesting area data
    har_i = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\2010_I_har.csv")#, index_col = ['x', 'y'])
    har_r = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\2010_R_har.csv")#, index_col = ['x', 'y'])

    for rcp in rcp_list:
        
        for time in time_list:
            
            file_dir = os.path.join(base_dir, rcp, time)
            for water in water_supply:
                if water == "irrigated":
                    expr = "200a_yld"
                    water_out = "I"
                    prd_df = har_i.drop(['spatial_ref', 'band'],axis = 1)
                elif water == "rainfed":
                    expr = "200b_yld"
                    water_out = "R"
                    prd_df = har_r.drop(['spatial_ref', 'band'],axis = 1)
                    
                    
                list_of_files = search_files(file_dir, expr)
                
    
    
                for counter, file in enumerate(list_of_files):
                    if counter < 1: 
                        # open tifs into as array for each pixel
                        rds = rioxarray.open_rasterio(file)
                        # translate that to dataframe, name the value column according 
                        df = rds.to_dataframe(file[80:84])
                        
                    else:
                        rds = rioxarray.open_rasterio(file)
                        # left_join here 
                        df = df.join(rds.to_dataframe(file[80:84]), how = "left", rsuffix="DROP").filter(regex="^(?!.*DROP)")
                
                #replace missing values:
                df.replace(-9, 0, inplace = True)
                df = df.groupby(by=crop_dict,axis=1).mean()
                # mean or median?
                df.reset_index(inplace = True)
                """
                In order to match data for multiplication it is important 
                to match index -> and in this case round 
                """
                df = df.round({'x': 6, 'y':6})
                df.set_index(['x', 'y'], inplace = True)
                # drop unneeded cols
                df.drop('band', axis = 1, inplace = True)
                # sort the cols for multipli?
                df.sort_index(axis = 1, inplace = True)
                
                prd_df = prd_df.round({'x':6, 'y':6})
                prd_df.set_index(['x', 'y'], inplace = True)
                prd_df.sort_index(axis = 1, inplace = True)
               
                # multiply with harvesting area
                df = df.mul(prd_df) 
                
                # normally write csv now, but to save memory skip next line
                #df.to_csv(out_dir + "/" + rcp +  "_" + time + "_" + water_out + ".csv")
                
                df.drop(['veg', 'nes', 'frt'], axis = 1, inplace = True)
                # sum each column with it's corresponding value
                df = df.mul(crop_value) 
                # sum the value for each cell
                df = df.sum(axis = 1)
                # write value csv
                df.to_csv(out_dir + "/" + "value_" + rcp +  "_" + time + "_" + water_out + ".csv")
#%% load in dictionary to aggregate crops:
crop_names = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\gaez_dictionary_future_attainable_yields.csv")
crop_names['current_code'] = crop_names['current_code'].str.lower()
name_dic = crop_names.set_index('gaez_code').to_dict()['current_code']

# read in crop values 
value_df = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\gaez_dictionary_current_data.csv")
# for the columns that have a too large span of value -> NA 
value_df.dropna(inplace = True)
value_df['gaez_code'] = value_df['gaez_code'].str.lower()
value_dic = value_df.set_index('gaez_code').to_dict()['price']
#%% 
# define outdir 
out_dir = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data"
# run function / 
merger_future(out_dir, name_dic, value_dic)

#%% new approach for current data

"""
As current production and future potential yields do not seem to measure the 
same thing: use potential yield with same assumptions of today...
and multiply with current harvesting areas
"""

# 
def merger_current(crop_dict):
    base_dir = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\current_yields"
    out_dir = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data"
    water_supply = ["irrigated", "rainfed"]
    # read in harvesting area data
    har_i = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\2010_I_har.csv")#, index_col = ['x', 'y'])
    har_r = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\2010_R_har.csv")#, index_col = ['x', 'y'])
    for water in water_supply:
        if water == "irrigated":
            expr = "200a_yld"
            water_out = "I"
            prd_df = har_i.drop(['spatial_ref', 'band'],axis = 1)
        elif water == "rainfed":
            expr = "200b_yld"
            water_out = "R"
            prd_df = har_r.drop(['spatial_ref', 'band'],axis = 1)
            
            
        list_of_files = search_files(base_dir, expr)
        for counter, file in enumerate(list_of_files):
            if counter < 1: 
                # open tifs into as array for each pixel
                rds = rioxarray.open_rasterio(file)
                # translate that to dataframe, name the value column according 
                df = rds.to_dataframe(file[67:71])
                
            else:
                rds = rioxarray.open_rasterio(file)
                # left_join here 
                df = df.join(rds.to_dataframe(file[67:71]), how = "left", rsuffix="DROP").filter(regex="^(?!.*DROP)")
        
        #replace missing values:
        df.replace(-9, 0, inplace = True)
        df = df.groupby(by=crop_dict,axis=1).mean()
        # mean or median?
        df.reset_index(inplace = True)
        """
        In order to match data for multiplication it is important 
        to match index -> and in this case round 
        """
        df = df.round({'x': 6, 'y':6})
        df.set_index(['x', 'y'], inplace = True)
        # drop unneeded cols
        df.drop('band', axis = 1, inplace = True)
        # sort the cols for multipli?
        df.sort_index(axis = 1, inplace = True)
        
        prd_df = prd_df.round({'x':6, 'y':6})
        prd_df.set_index(['x', 'y'], inplace = True)
        prd_df.sort_index(axis = 1, inplace = True)
       
        # multiply with harvesting area
        df = df.mul(prd_df) 
        
        # normally write csv now, but to save memory skip next line
        df.to_csv(out_dir + "/" + "current" +  "_prod_" + water_out + ".csv")
        
        
#%% run 

merger_current(name_dic)

