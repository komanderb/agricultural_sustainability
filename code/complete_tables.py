# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 11:05:36 2022

@author: Bjoern Komander

File for creating the final tables, including population, gdp
caloric yield, etc.
"""
#%% load relevant libraries

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

#%% first function to create base tables

"""
Important note: For the first approach I'm still using
the prices from 2000, caloric yield that might not be too precise 
as well
GDP for 2005 
Population for 2005
Also the function is designed to take into account changing values 
for price, caloric yield as well as including more gdp, population data

"""

def current_table(dictionary_list, name_list, drop_list, 
                  file_list, variables):
    #global stuff
    drop = ['band', 'spatial_ref']
    
    # current production dataframes 
    df_i = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\current_prod_I.csv", 
                       index_col=['x', 'y'])
    df_r = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\current_prod_R.csv",
                       index_col=['x', 'y'])
    
    # and list 
    current_list = [df_i, df_r]
    water = ['i', 'r']
    
    # first all make all the different summations of production
    for counter, item in enumerate(dictionary_list):
        # first for total produced: 
        if counter < 1:
            df = df_i.sum(axis = 1).to_frame().rename(columns = {0:"prd_i"})
            
            df = df.join(df_r.sum(axis = 1).rename('prd_r'), how = 'left')
         
        
        for i, data in enumerate(current_list):
            process_df = current_list[i].drop(drop_list[counter], axis = 1)
            process_df = process_df.mul(item)
            df = df.join(process_df.sum(axis = 1).rename(name_list[counter] + "_" + water[i]),
                                                         how = 'left')
    
    
                        
    # merge with gdp and population data
    for counter, item in enumerate(file_list):
        rds = rioxarray.open_rasterio(item)
        df_join = rds.to_dataframe(variables[counter])
        df_join.reset_index(inplace = True)
        df_join.drop(drop, axis = 1, inplace = True)
        df_join = df_join.round({'x':6, 'y':6})
        df_join.set_index(['x', 'y'], inplace = True)
        # join with current data 
        df = df.join(df_join, how = 'left')
        
        
    
    # after all is finished -> drop rows with missing data 
    # for memory efficiency! 
    check = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\overview_df.csv", 
                        index_col=['x', 'y'])
    df = df.join(check['missing'], how = 'left')
    df = df[df.missing == 0]
    out = r"G:\Meine Ablage\agricultural_sustain\final_tables\current_data.csv"
    df.to_csv(out)
    
#%% make relevant dictionaries: 
# value and caloric yield

dict_df = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\gaez_dictionary_current_data.csv")
dict_df['gaez_code'] = dict_df['gaez_code'].str.lower()
value_df = dict_df[['gaez_code', 'price']].dropna()        
caloric_df = dict_df[['gaez_code', 'cal_yld']].dropna()
cash_df = dict_df[['gaez_code', 'price', 'type']].dropna()
cash_df = cash_df[cash_df.type == 'cash']   
caloric_df['cal_yld'] = caloric_df.cal_yld * 10000    

# make dictionaries:    
value_dic = value_df.set_index('gaez_code').to_dict()['price']
cal_dic = caloric_df.set_index('gaez_code').to_dict()['cal_yld']
cash_dic = cash_df.set_index('gaez_code').to_dict()['price']

# make the relevant lists

dic_list = [value_dic, cal_dic, cash_dic]
variable_name = ['value', 'cal_yld', 'cash_value']

# make list of drop lists:
drop_value = list(set(dict_df.gaez_code) - set(value_df.gaez_code))   
drop_cal = list(set(dict_df.gaez_code) - set(caloric_df.gaez_code)) 
drop_cash = list(set(dict_df.gaez_code) - set(cash_df.gaez_code))

drop_list = [drop_value, drop_cal, drop_cash]

# for gdp and population

files = [r"G:\Meine Ablage\agricultural_sustain\gdp\gridded_gdp\GDP2005.tif",
         r"G:\Meine Ablage\agricultural_sustain\population\population_2005.tif"]

names = ['gdp', 'pop']

#%% run 

current_table(dic_list, variable_name, drop_list, files, names)
#%% check the output

test = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\final_tables\current_data.csv")


test.mean()

# missing data value
#%% future tables 

def final_table(crop_dict, dictionary_list, name_list, drop_list):
    
    base_file = r"G:\Meine Ablage\agricultural_sustain\final_tables\current_data.csv"
    base_df = pd.read_csv(base_file, index_col = ['x', 'y'])
    
    base_dir = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\future_yields"
    
    rcp_list = ["rcp2p6", "rcp4p5", "rcp6p0", "rcp8p5"]
    time_list = ["2020sH", "2050sH", "2080sH"]
    water_supply = ["irrigated", "rainfed"]
    # read in harvesting area data
    har_i = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\2010_I_har.csv")#, index_col = ['x', 'y'])
    har_r = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\2010_R_har.csv")#, index_col = ['x', 'y'])

    # iterate through different combinations of rcp and time 
    for rcp in rcp_list:
        
        for decade in time_list:
            file_dir = os.path.join(base_dir, rcp, decade)
            for water in water_supply:
                if water == "irrigated":
                    expr = "200a_yld"
                    water_out = "i"
                    prd_df = har_i.drop(['spatial_ref', 'band'],axis = 1)
                elif water == "rainfed":
                    expr = "200b_yld"
                    water_out = "r"
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
                        # left join new data to existing df 
                        df = df.join(rds.to_dataframe(file[80:84]), how = "left", rsuffix="DROP").filter(regex="^(?!.*DROP)")
                # replace missing data -> messes up the aggregation
                df.replace(-9, 0, inplace = True)
                df = df.groupby(by=crop_dict,axis=1).mean()
                # mean or median?
                df.reset_index(inplace = True)
                
                
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
                
                
                # now make all the variables:
                for counter, item in enumerate(dictionary_list):
                    # first for total produced: 
                    if counter < 1:
                        f_df = df.sum(axis = 1).to_frame().rename(columns = 
                                                                  {0: "prd_" + rcp + "_" +
                                                                   decade + 
                                                                   "_" + water_out})
                        
                        
                     
                    
                   
                    process_df = df.drop(drop_list[counter], axis = 1)
                    process_df = process_df.mul(item)
                    f_df = f_df.join(process_df.sum(axis = 1).rename(name_list[counter] + "_" + 
                                                                    rcp + "_" +
                                                                     decade +
                                                                    "_" + water_out),
                                                                 how = 'left')
                
                    

                base_df = base_df.join(f_df, how = 'left')
                
    
    out = r"G:\Meine Ablage\agricultural_sustain\final_tables\final_table.csv"
    base_df.to_csv(out)
                
#%% crop dictionary

crop_names = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\gaez_dictionary_future_attainable_yields.csv")
crop_names['current_code'] = crop_names['current_code'].str.lower()
name_dic = crop_names.set_index('gaez_code').to_dict()['current_code']

#%% run 

final_table(name_dic, dic_list, variable_name, drop_list)
    
#%% check output

check_df =  pd.read_csv( r"G:\Meine Ablage\agricultural_sustain\final_tables\final_table.csv", index_col = ['x', 'y'])   

check_df.mean()
#%% 

check_df.columns


check_df['cal_yld_r'].max() / (365 * 2700)
