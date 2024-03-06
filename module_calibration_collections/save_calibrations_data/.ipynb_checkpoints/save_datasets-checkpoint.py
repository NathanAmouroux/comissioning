import numpy as np
import lsst.daf.butler as dafButler
import pickle
import sys
import os
from configparser import ConfigParser
import find_by_chain

class datas:
    def __init__(self, collection=None, calib = 'flat', repo = 'embargo', exp = 'LATISS', is_chained = True):
        self.config = ConfigParser()
        self.config.read("/sdf/data/rubin/user/amouroux/comissioning/module_calibration_collections/config.ini")
        self.repo = self.config.get('base', repo + '_repo')
        self.collection = collection
        self.exp = exp
        self.calib = calib
        self.is_chained = is_chained
        #self.outpath = config.get(self.exp, 'base_save_path') + 'saved_collections/paths/' + f"{self.collection.split('/')[-1]}"
            
    def open_butler(self, collection = None):
        #self.collection = collection
        butler = dafButler.Butler(self.repo, collections=collection)
        #self.registry = butler.registry
        return butler
        
    def get_datasets(self, collection, exp, calib, is_chained):
        if is_chained:
            get_coll = find_by_chain.get_collections(collection = collection, exp = exp, calib = calib)
            datasets = get_coll.find_datasets()
        else : 
            datasets = list(self.open_butler(collection).registry.queryDatasets(calib.split('-')[0], collections = exp + "/calib"))
        return datasets[0]

    def open_datasets(self, collection, exp, calib, is_chained, detector):
        butler = self.open_butler(collection = collection)
        dataset = self.get_datasets(collection = collection, exp = exp, calib = calib, is_chained = is_chained)
        if calib.split("-")[0] == "flat":
            physical_filter = dataset.dataId["physical_filter"]
            file = butler.get("flat", instrument=exp, physical_filter=physical_filter, detector=detector, collections=dataset.run)
        else : 
            file = butler.get(calib, instrument=exp, detector=detector, collections=dataset.run)
        return file

    def get_array(self, collection, exp, calib, is_chained, detector):
        allowed_colls = ["flat", "dark", "bias"]
        if calib.split("-")[0] not in allowed_colls:
            print(f"Warning, allowed collections with this function are {allowed_colls}")
        file = self.open_datasets(collection, exp, calib, is_chained, detector)
        data = file.getImage().getArray()
        return data
    def get_defects(self, collection, exp, calib, is_chained, detector):
        file = self.open_datasets(collection, exp, calib, is_chained, detector)
        data = file.toTable()[0]
        return data
    def get_crosstalk(self, collection, exp, calib, is_chained, detector):
        file = self.open_datasets(collection, exp, calib, is_chained, detector)
        data = file.coeffs
        return data

    def save_calibration_data(self, collection, exp, calib, is_chained, detector, outpath = None):
        if calib.split("-")[0] =="flat" or calib =="dark" or calib == "bias":
            data = self.get_array(collection, exp, calib, is_chained, detector)
        elif calib == "defects":
            data = self.get_defects(collection, exp, calib, is_chained, detector)
        elif calib == "crosstalk":
            data = self.get_crosstalk(collection, exp, calib, is_chained, detector)
        if outpath == None : 
            outpath = self.config.get(self.exp, 'base_save_path') + 'saved_collections/datas/' + f"{collection.split('/')[-1]}/"
        if not os.path.exists(outpath):
            os.mkdir(outpath)
        print(f"data outpath will be {outpath}" +  f"{calib}_{detector}_data.pkl")
        with open(outpath+f"{calib}_{detector}_data.pkl", 'wb') as file:
            pickle.dump(data, file)
        return data