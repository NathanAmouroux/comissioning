import numpy as np
import lsst.daf.butler as dafButler
import pickle
import os
from configparser import ConfigParser
import find_by_chain

class Data:
    def __init__(self, collection=None, calib = 'flat', detector = 0, repo = 'embargo', exp = 'LATISS', is_chained = True):
        self.config = ConfigParser()
        self.config.read("../config.ini")
        self.repo = repo
        self.repo_path = self.config.get('base', repo + '_repo')
        self.exp = exp
        if collection is None:
            self.collection = self.config.get(self.exp, "current_collection")
        else:
            self.collection = collection
        self.is_chained = is_chained
        self.calib = calib
        self.detector = detector
        #self.outpath = config.get(self.exp, 'base_save_path') + 'saved_collections/paths/' + f"{self.collection.split('/')[-1]}"
            
    def open_butler(self):
        butler = dafButler.Butler(self.repo_path, collections=self.collection)
        return butler
        
    def get_datasets(self):
        if self.is_chained:
            get_coll = find_by_chain.get_collections(collection = self.collection, calib = self.calib, repo = self.repo, exp = self.exp)
            datasets = get_coll.find_datasets()
        else : 
            datasets = list(self.open_butler(self.collection).registry.queryDatasets(self.calib.split('-')[0], collections = self.exp + "/calib"))
        return datasets[0]

    def open_datasets(self):
        butler = self.open_butler()
        dataset = self.get_datasets()
        if self.calib.split("-")[0] == "flat":
            physical_filter = dataset.dataId["physical_filter"]
            file = butler.get("flat", instrument=self.exp, physical_filter=physical_filter, detector=self.detector, collections=dataset.run)
        else : 
            file = butler.get(self.calib, instrument=self.exp, detector=self.detector, collections=dataset.run)
        return file

    def get_array(self):
        allowed_colls = ["flat", "dark", "bias"]
        if self.calib.split("-")[0] not in allowed_colls:
            print(f"Warning, allowed collections with this function are {allowed_colls}")
            #raise error
        file = self.open_datasets()
        data = file.getImage().getArray()
        return data
    
    def get_defects(self):
        file = self.open_datasets()
        data = file.toTable()[0]
        return data
    
    def get_crosstalk(self):
        file = self.open_datasets()
        data = file.coeffs
        return data

    def save_calibration_data(self, outpath = None):
        if self.calib.split("-")[0] =="flat" or self.calib =="dark" or self.calib == "bias":
            data = self.get_array()
        elif self.calib == "defects":
            data = self.get_defects()
        elif self.calib == "crosstalk":
            data = self.get_crosstalk()
        if outpath is None : 
            outpath = self.config.get(self.exp, 'base_save_path') + 'saved_collections/datas/' + f"{self.collection.split('/')[-1]}/"
        if not os.path.exists(outpath):
            os.mkdir(outpath)
        print(f"Data outpath will be {outpath}" +  f"{self.calib}_{self.detector}_data.pkl")
        with open(outpath+f"{self.calib}_{self.detector}_data.pkl", 'wb') as file:
            pickle.dump(data, file)
        return data