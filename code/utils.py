# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 09:53:02 2022

@author: Björn Komander


Script with supporting functions
"""
import os
import re


#%% 
def search_files(directory:str, pattern:str='.') -> list:
    """
    

    Parameters
    ----------
    directory : str
        File directiory to return.
    pattern : str, optional
        DESCRIPTION. The default is '.'.

    Returns
    -------
    list
        sorted list of files in directory.

    """
    files = list()
    for root, _, file_names in os.walk(directory):
        for file_name in file_names:
            files.append(os.path.join(root, file_name))
    files = list(filter(re.compile(pattern).search, files))
    files.sort()
    # sorting files with numbers as strings does not sort them de or increasing
    return files
