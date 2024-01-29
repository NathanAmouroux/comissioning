import numpy as np
import lsst.daf.butler as dafButler
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import sys
######Compare metadata of an exposure of the selected collection to caliubration collections found via butler
repo = '/sdf/group/rubin/repo/main/butler.yaml'
butler = dafButler.Butler(repo)
registry = butler.registry
print("Butler successfuly instatiated")
collection = "LATISS/runs/AUXTEL_DRP_IMAGING_2023-11A-10A-09AB-08ABC-07AB-05AB/w_2023_46/PREOPS-4553"
#collection = sys.argv[1]

def test_for_calibration(butler, collection, calibration_type) :
    ## This function just tries to get a defect from the collection.
    ## If successfull it passes True, otherwise False.
    try :
        butler.get(calibration_type, instrument='LATISS', physical_filter='SDSSr_65mm~empty', detector=0, collections=collection)
        exists = True
    except :
        exists = False
    return exists

butler = dafButler.Butler(repo, collections=collection)
registry = butler.registry
#####
def get_chain(collection):
    chain = registry.getCollectionChain(collection)
    calibs = [c for c in sorted(chain, reverse = True) if "LATISS/calib" in c]
    return calibs

calib_chain = get_chain(collection)
with open(f'{collection}_calibrations_chained.txt', 'w') as f:
    for col in calib_chain:
        f.write(f"{col}\n")
print("Chained calibrations are the following :")
for c in calib_chain:
    print(c)
print("\n\n")
#####
c_types = np.array(["flat-i", "flat-z", "flat-y", "flat-g", "flat-r", "bias", "defects", "dark", "crosstalk"])

calib_types, calib_names = [], []
for i, element in enumerate(calib_chain):
    for calib_t in c_types:
        if calib_t in element and calib_t not in calib_types:
            print(f"Found {calib_t}.")
            calib_types.append(calib_t)
            calib_names.append(element)
with open(f'{collection}_last_calibrations.txt', 'w') as f:
    for col1, col2 in np.column_stack((calib_names, calib_types)):
        f.write(f"{col1}\t{col2}\n")
####
datasets = []
calib_colls = []
physical_filters = []
for cal_n, cal_t in np.column_stack((calib_names, calib_types)):
    print(cal_n, cal_t)
    if "flat" in cal_t:
        dataset = list(registry.queryDatasets("flat", collections = cal_n))
        physical_filters.append(dataset[0].dataId["physical_filter"])
    else :
        dataset = list(registry.queryDatasets(cal_t, collections = cal_n))
        physical_filters.append(0) #For convenient saving later
    datasets.append(dataset)
    coll_paths.append(dataset[0].run)
print("\n", datasets, "\n\n", coll_paths, "\n\n", physical_filters)
with open(f'{collection}_calibrations_access.txt', 'w') as f:
    for col1, col2 in np.column_stack((coll_paths, physical_filters)):
        f.write(f"{col1}\t{col2}\n")
####
"""
calib_arr = [[] for i in range(len(coll_paths))]
for i, cal_n in enumerate(coll_paths):
    if "flat" not in calib_types_copy[i] :     
        file = butler.get(calib_types_copy[i], instrument='LATISS',detector=0, collections=cal_n)
        if calib_types_copy[i]=="bias" or calib_types_copy[i]=="dark":
            calib_arr[i] = file.getImage().getArray()
        if calib_types_copy[i]=="defects" :
            print("defects!")
            calib_arr[i] = file.toTable()[0]
        if calib_types_copy[i]=="crosstalk":
            print("crosstalk!")
            calib_arr[i] = file.coeffs
    else : 
        calib_arr[i] = butler.get("flat", instrument='LATISS', physical_filter=physical_filters[i] , detector=0, collections=cal_n)
        calib_arr[i] = calib_arr[i].getImage().getArray()
"""
