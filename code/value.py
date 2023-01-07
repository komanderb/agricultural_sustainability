# -*- coding: utf-8 -*-
"""
Created on Fri Dec  9 18:34:10 2022

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

#%% make actual value df:
    
# for dropping unncessary data 
overview_df = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\overview_df.csv",
                           index_col = ['x', 'y'])

# value
dict_df = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\gaez_dictionary_current_data.csv")
dict_df['gaez_code'] = dict_df['gaez_code'].str.lower()
value_df = dict_df[['gaez_code', 'price']].dropna()        

drop_value = list(set(dict_df.gaez_code) - set(value_df.gaez_code))   
value_dic = value_df.set_index('gaez_code').to_dict()['price']

# total production
production = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\2010_T_prd.csv")
production = production.round({'x':6, 'y':6})
drop_value.extend(['band', 'spatial_ref'])

production.drop(drop_value, axis = 1, inplace = True)

production.set_index(['x', 'y'], inplace = True)

production = production.mul(value_dic)
production  = production.sum(axis = 1).to_frame().rename(columns = 
                                          {0: "prd_value"})

df = production.join(overview_df['missing'], how = 'left')
df = df[df.missing != 1]
df.drop('missing', axis = 1, inplace = True)

df.to_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\2010total_value.csv")
