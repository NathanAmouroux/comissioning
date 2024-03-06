import numpy as np
import lsst.daf.butler as dafButler
import sys
import os
from configparser import ConfigParser
"""
This func has a problem with flats to fix/investigate :
1) With one exposure you only get to access one band of flat
2) The path of the found flat is not complete so butler doesn't find them

Otherwize it works
"""

## Get configs
class get_collections:
    def __init__(self, collection=None, calib = 'all', repo = 'embargo', exp = 'LATISS'):
        config = ConfigParser()
        config.read("/sdf/data/rubin/user/amouroux/comissioning/module_calibration_collections/config.ini")
        self.repo = config.get('base', repo + '_repo')
        self.collection = collection
        self.exp = exp
        self.calib = calib
        #self.outpath = config.get(self.exp, 'base_save_path') + 'save_collections/paths/' + f"{self.collection.split('/')[-1]}"
            
    def open_butler(self, collection = None):
        #self.collection = collection
        butler = dafButler.Butler(self.repo, collections=collection)
        #self.registry = butler.registry
        return butler
        
    def find_exposures(self, collection = None): #Pb here : this finds only one flat band
        butler = self.open_butler()
        registry = butler.registry
        exps = registry.queryDatasets('postISRCCD', instrument=self.exp, where="exposure.day_obs>20211001", collections = collection)
        for i, ref in enumerate(exps):
            if i > 0:
                break
            print(ref.dataId.full)
            exposure = ref.dataId.full["exposure"]
        return exposure


    def open_Metadata(self, collection = None):
        if collection == None :
            collection = self.collection
        exposure, butler = self.find_exposures(collection), self.open_butler(collection=collection)
        if self.exp == "LATISS":
            expMetadata = [butler.get('postISRCCD.metadata',instrument=self.exp, detector=0, exposure=exposure, collections=collection)]
        else : 
            expMetadata = []
            for i in range(9):
                expMetadata_ = butler.get('postISRCCD.metadata',instrument=self.exp, detector=i, exposure=exposure, collections=collection)
                expMetadata.append(expMetadata_)
        return expMetadata
        
    def find_calibrations(self, collection = None, calib=None):
        if collection == None :
            collection = self.collection
        elif calib == None :
            calib = self.calib
        #c_list = np.array(["flat-i", "flat-z", "flat-y", "flat-g", "flat-r", "flat-u", "bias", "defects", "dark", "crosstalk"]) #Exhaustive list; find a way to include every flats
        c_list = np.array(["flat", "bias", "defects", "dark", "crosstalk"])
        if calib == 'all':
            c_types = c_list
        else : 
            c_types = np.array(calib)
            for i in range(len(c_types)):
                if c_types[i] not in c_list:
                    print("Warning bad calibration selected or maybe you misspelled it ?!")
        calib_types, calib_names = [], []
        expMetadata = self.open_Metadata(collection = collection)
        for i, element in enumerate(c_types):
            for j in range(len(expMetadata)):
                curr_calib = expMetadata[j][f"LSST CALIB RUN {element.upper()}"]
                print(f"Found {element}.")
                calib_names.append(curr_calib)
                calib_types.append(element) ##Will contain duplicates
        return calib_types, calib_names

    def find_datasets(self, collection = None, calib = None):
        if collection == None :
            collection = self.collection
        elif calib == None :
            calib = self.calib
        calibrations_types, calibration_names = self.find_calibrations(collection, calib)
        datasets, physical_filters = [], []
        for i, calibration_name in enumerate(calibration_names):
            if "flat" in calibrations_types[i].split('-'):
                dataset = list(self.open_butler(collection = calibration_name).registry.queryDatasets("flat", collections = calibration_name))
                datasets.append(dataset)
                physical_filters.append(dataset[0].dataId["physical_filter"])
            else : 
                datasets.append(list(self.open_butler(collection = calibration_name).registry.queryDatasets(calibrations_types[i], collections = calibration_name)))
                physical_filters.append(0)
        return datasets, physical_filters

    def save_datasets_paths(self, collection = None, calib = None):
        if collection == None :
            collection = self.collection
        elif calib == None :
            calib = self.calib
        datasets, physical_filters = self.find_datasets(collection, calib)
        with open(outpath + '_last_calibrations.txt', 'w') as f:
            for col1, col2 in np.column_stack((datasets, physical_filters)):
                f.write(f"{col1}\t{col2}\n")