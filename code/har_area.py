# -*- coding: utf-8 -*-
"""
Just one file for getting the total harvesting area

@author: lenovo
"""
#%% import libs 
import pandas as pd
#%% process data 
irrigated = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\2010_I_har.csv"
rainfed = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\2010_R_har.csv"
# read in data
df_i = pd.read_csv(irrigated)
df_r = pd.read_csv(rainfed)

data_list = [df_i, df_r]
drop = ['band', 'spatial_ref']

for counter, i in enumerate(data_list):
    data_list[counter].drop(drop, axis = 1, inplace = True)
    # round index 
    data_list[counter] = data_list[counter].round({'x':6, 'y':6})
    data_list[counter].set_index(['x', 'y'], inplace = True)
    data_list[counter] = data_list[counter].sum(axis = 1)
    data_list[counter] = data_list[counter].to_frame().rename(columns = {0:"har"})

merged_data = data_list[0].join(data_list[1], how = "left", rsuffix = "_r")
merged_data = merged_data.sum(axis = 1).to_frame().rename(columns = {0: "har_area"})   
#%% write data 
merged_data.har_area = merged_data.har_area * 1000
merged_data[merged_data.har_area > 0]
import seaborn as sns
sns.kdeplot(data=merged_data[merged_data.har_area > 0], x="har_area", fill = True, alpha = 0.5)
