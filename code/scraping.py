# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 10:37:34 2022

@author: Bjoern Komander 

File to scrape the gaez data. As we only realized later that we need 
Agro-Climatic potential yields for today, they are not included in the main function.
# Also a different environment has been used. See dependencies for more info.
"""
#%% libraries
import pandas as pd
import numpy as np
import os
# scraping
import selenium
from selenium import webdriver
#pip install webdriver-manager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
from time import sleep
#%% read in crop names

crop_names = pd.read_csv(r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\gaez_dictionary_future_attainable_yields.csv")
crop_names = crop_names['gaez_code'].to_list()
#%% function 

def link_scraper(crops):
    
    
    # baseline 
    base_link = "https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res02/HadGEM2-ES/"
    
    base_dir = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\future_yields"
    
    # different concentration pathways
    rcp_list = ["rcp2p6", "rcp4p5", "rcp6p0", "rcp8p5"]
    # different decades
    time_list = ["2020sH", "2050sH", "2080sH"]
    # different water_supplies
    water_supply = ["200a_yld.tif", "200b_yld.tif"]
    
    # nested loop
    for rcp in rcp_list:
        
        for time in time_list:
            file_dir = os.path.join(base_dir, rcp, time)
            os.makedirs(file_dir, exist_ok=True)
            
            # for selenium browser make download settings
            options = Options()
            options.add_experimental_option("prefs", {
              "download.default_directory": file_dir,
              "download.prompt_for_download": False,
              "download.directory_upgrade": True,
            "safebrowsing.enabled": True
            })
            
            # open browser
            browser = webdriver.Chrome(ChromeDriverManager().install(), 
                                       chrome_options= options)
            
            for water in water_supply:
                
                for crop in crops:
                    
                    filename = crop + water 
                    
                    file_link = base_link + rcp + "/" + time + "/" + filename 
                    
                    browser.get(file_link)
            
            sleep(120)
            browser.close()
                    

#%% run 

link_scraper(crop_names)

#%% part two - only current data 

"""
It is only one link (no different RCP's). Therefore new function
                     
"""

# directory to save data 
file_dir = r"G:\Meine Ablage\agricultural_sustain\GAEZ_data\data\current_yields"
water_supply = ["200a_yld.tif", "200b_yld.tif"]
base_link = "https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res02/CRUTS32/Hist/8110H/"
 # for selenium browser make download settings
options = Options()
options.add_experimental_option("prefs", {
  "download.default_directory": file_dir,
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
"safebrowsing.enabled": True
})

# open browser
browser = webdriver.Chrome(ChromeDriverManager().install(), 
                           chrome_options= options)

for water in water_supply:
    
    for crop in crop_names:
        
        filename = crop + water 
        
        file_link = base_link  + filename 
        
        browser.get(file_link)


# run 

                    
                    
                    
                    