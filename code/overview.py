# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 11:08:12 2022

@author: Bjoern Komander

This script is to create an overview dataframe:
1. Unique Cell identifyer for memory efficiency 
2. Dummy for if cell is missing data (ocean, desert)
3. Dummy for if no production is in cell 2010
 
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

from utils import search_files#


#%% 

# load in dataframe -> use future yield as missing data is -9
example = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\future_yields\rcp2p6\2020sH\yyam200b_yld.tif"
rds = rioxarray.open_rasterio(example)
 
df = rds.to_dataframe('a')
df['missing'] = np.where(df['a'] == -9, 1, 0)
df['missing'].value_counts()
# over 7 million cells with no data
# load in production data (total)

total_production = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\2010_T_prd.csv")

# then do the usual stuff -> drop irrelevant columns
drop = ['band', 'spatial_ref']
df.reset_index(inplace = True)
df.drop(drop, axis = 1, inplace = True)
total_production.drop(drop, axis = 1, inplace = True)

df = df.round({'x':6, 'y':6})
total_production = total_production.round({'x':6, 'y':6})
# sort the cols for multipli?
df.set_index(['x', 'y'], inplace = True)
total_production.set_index(['x', 'y'], inplace = True)

total_production = total_production.sum(axis = 1)
total_production = total_production.to_frame().rename(columns = {0:"value_"})

# join the two
df = df.join(total_production, how = 'left')

df['production'] = np.where(((df['missing'] == 0) & (df['value_'] == 0)), 1, 0)

df.production.sum()

df.drop('value_', axis = 1, inplace = True)

df['cell_id'] = np.arange(len(df))

df.drop('a', axis = 1, inplace = True)

# write to csv
out = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\overview_df.csv"
df.to_csv(out)

# 
a = rasterio.open(file_current)
a.profile
