import numpy as np
import lsst.daf.butler as dafButler
import sys
import os
from configparser import ConfigParser

class get_collections:
    def __init__(self, collection=None, calib = 'flat', repo = 'embargo', exp = 'LATISS'):
        config = ConfigParser()
        config.read("/sdf/data/rubin/user/amouroux/comissioning/module_calibration_collections/config.ini")
        self.repo = config.get('base', repo + '_repo')
        self.collection = collection
        self.exp = exp
        self.calib = calib
        self.outpath = config.get(self.exp, 'base_save_path') + 'save_collections/paths/' + f"{self.collection.split('/')[-1]}"
            
    def open_butler(self, collection = None):
        #self.collection = collection
        butler = dafButler.Butler(self.repo, collections=collection)
        registry = butler.registry
        return registry
        
    def get_chain(self, collection = None):
        chain = self.open_butler().getCollectionChain(collection)
        calibs = [c for c in sorted(chain, reverse = True) if self.exp + "/calib" in c] #Can be a problem in the future if path differs
        return calibs

    def find_calibrations(self, collection = None, calib=None):
        if collection == None :
            collection = self.collection
        elif calib == None :
            calib = self.calib
            
        c_list = np.array(["flat-i", "flat-z", "flat-y", "flat-g", "flat-r", "flat-u", "bias", "defects", "dark", "crosstalk"]) #Exhaustive list      
        if calib not in c_list:
            print(f"Warning bad calibration selected or maybe you misspelled it ?!\nAvaible calibs are {c_list}")
        assert(calib in c_list)
        calib_chain = self.get_chain(collection)
        calib_type = "0"
        for i, element in enumerate(calib_chain):
            if calib in element and calib != calib_type:
                print(f"Found {calib}. Its name is {element}")
                calib_type = calib
                calib_name = element
        if calib_type == calib:
            return calib_type.split("-")[0], calib_name
        else :
            print(f"Calibration {calib} not found.")
            raise ValueError(f"\033[91m{calib} does not exist in this collection\033[0m")
            

    def find_datasets(self, collection = None, calib = None):
        if collection == None :
            collection = self.collection
        elif calib == None :
            calib = self.calib
        try:
            calibration_type, calibration_name = self.find_calibrations(collection, calib)
            dataset = list(self.open_butler(collection = calibration_name).queryDatasets(calibration_type, collections = calibration_name))
            return dataset
        except ValueError as e:
            print(f"The above exception has been raised {e}")
            return

    def save_datasets_paths(self, collection = None, calib = None):
        if collection == None :
            collection = self.collection
        elif calib == None :
            calib = self.calib
        dataset = self.find_datasets(collection, calib)
        with open(outpath + '_chained_calibrations.txt', 'w') as f:
            for col1, col2 in np.column_stack((datasets, physical_filters)):
                f.write(f"{col1}\t{col2}\n")