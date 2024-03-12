import numpy as np
import lsst.daf.butler as dafButler
import sys
import os
from configparser import ConfigParser

class get_collections:
    def __init__(self, collection=None, calib=None, repo = 'embargo', exp = 'LATISS'):
        self.config = ConfigParser()
        self.config.read("/sdf/data/rubin/user/amouroux/comissioning/module_calibration_collections/config.ini")
        self.repo = repo
        self.repo_path = self.config.get('base', repo + '_repo')
        self.exp = exp
        if collection is None:
            self.collection = self.config.get(self.exp, "current_collection")
        else:
            self.collection = collection
        self.calib = calib
        
            
    def open_butler(self, collection = None):
        if collection is None:
            collection = self.collection
        butler = dafButler.Butler(self.repo_path, collections=self.collection)
        registry = butler.registry
        return registry
        
    def get_chain(self):
        chain = self.open_butler().getCollectionChain(self.collection)
        calibs = [c for c in sorted(chain, reverse = True) if self.exp + "/calib" in c] #Can be a problem in the future if path differs
        return calibs

    def find_calibrations(self):          
        c_list = np.array(["flat-i", "flat-z", "flat-y", "flat-g", "flat-r", "flat-u", "bias", "defects", "dark", "crosstalk"]) #Exhaustive list      
        if self.calib not in c_list:
            print(f"Warning bad calibration selected or maybe you misspelled it ?!\nAvaible calibs are {c_list}")
        assert(self.calib in c_list)
        calib_chain = self.get_chain()
        calib_type = "0"
        for element in calib_chain:
            if self.calib in element and self.calib != calib_type:
                print(f"Found {self.calib}. Its name is {element}")
                calib_type = self.calib
                calib_name = element
        if calib_type == self.calib:
            return calib_type.split("-")[0], calib_name
        else :
            print(f"Calibration {self.calib} not found.")
            raise ValueError(f"\033[91m{self.calib} does not exist in this collection\033[0m")
        return
            
    def find_datasets(self):
        try:
            calibration_type, calibration_name = self.find_calibrations()
            dataset = list(self.open_butler().queryDatasets(calibration_type, collections = calibration_name))
            return dataset
        except ValueError as e:
            print(f"The above exception has been raised {e}")
            return

    def save_datasets_paths(self, outpath = None):
        dataset = self.find_calibrations()
        if outpath is None:
            outpath = self.config.get(self.exp, 'base_save_path') + 'saved_collections/datas/' + f"{self.collection.split('/')[-1]}"
            if not os.path.exists(outpath):
                os.mkdir(outpath)
        with open(outpath + 'chained_calibrations_paths.txt', 'w') as f:
            for col1 in np.column_stack((dataset)):
                f.write(f"{col1}\n")