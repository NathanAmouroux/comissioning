import numpy as np
import lsst.daf.butler as dafButler
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import sys

repo = '/sdf/group/rubin/repo/main/butler.yaml'
butler = dafButler.Butler(repo)
registry = butler.registry
print("Butler successfuly instatiated")
calibration_type = sys.argv[1]

def test_for_calibration(butler, collection, calibration_type) :
    ## This function just tries to get a defect from the collection.
    ## If successfull it passes True, otherwise False.
    try :
        butler.get(calibration_type, instrument='LATISS', physical_filter='SDSSr_65mm~empty', detector=0, collections=collection)
        exists = True
    except :
        exists = False
    return exists

calibration_collections = [c for c in sorted(registry.queryCollections())  if test_for_calibration(butler, c, str(calibration_type))]

with open(f'{calibration_type}_collections.txt', 'w') as f:
    for col in calibration_collections:
        f.write(f"{col}\n")