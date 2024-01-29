import numpy as np
import lsst.daf.butler as dafButler
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import pickle
import sys

repo = '/sdf/group/rubin/repo/embargo/butler.yaml'
#collection = "LATISS/runs/AUXTEL_DRP_IMAGING_2023-11A-10A-09AB-08ABC-07AB-05AB/w_2023_46/PREOPS-4553"
collection = "LATISS/runs/AUXTEL_DRP_IMAGING_2023-09A-08ABC-07AB-05AB/d_2023_09_25/PREOPS-3780"
outpath = "/sdf/data/rubin/user/amouroux/comissioning/AuxTel/calibration_collections/save_load_collections_pckgs/" + f"{collection.split('/')[-1]}"

butler = dafButler.Butler(repo)
registry = butler.registry
print("Butler successfuly instatiated")

#collection = sys.argv[1]
calib_names, calib_types = np.loadtxt(outpath + "_last_calibrations.txt", dtype = 'str', delimiter = '\t',unpack=True)
coll_paths, physical_filters = np.loadtxt(outpath + "_calibrations_access.txt", dtype = 'str', delimiter = '\t',unpack=True)

calib_arr = [[] for i in range(len(coll_paths))]
for i, cal_n in enumerate(coll_paths):
    if "flat" not in calib_types[i] :     
        file = butler.get(calib_types[i], instrument='LATISS',detector=0, collections=cal_n)
        if calib_types[i]=="bias" or calib_types[i]=="dark":
            calib_arr[i] = file.getImage().getArray()
        if calib_types[i]=="defects" :
            print("defects!")
            calib_arr[i] = file.toTable()[0]
        if calib_types[i]=="crosstalk":
            print("crosstalk!")
            calib_arr[i] = file.coeffs
    else : 
        file = butler.get("flat", instrument='LATISS', physical_filter=physical_filters[i] , detector=0, collections=cal_n)
        calib_arr[i] = file.getImage().getArray()
"""
defects = calib_arr[np.where(calib_types=="defects")[0][0]]
msk = np.ones((4000,4072))
for defect in defects :
    x0  = defect['x0']
    y0  = defect['y0']
    width  = defect['width']
    height  = defect['height']
    for x in range(x0, x0 + width):
        for y in range(y0, y0 + height):
            msk[y][x] = 0
calib_arr.append(msk)
calib_types = np.append(calib_types, "defects_array")
"""
dict = {"calib_data":calib_arr, "calib_type":calib_types}
# Save the dictionary to a file using pickle
with open(outpath + "_data_calibration.pkl", 'wb') as file:
    pickle.dump(dict, file)

sys.exit()



    