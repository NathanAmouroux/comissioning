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
physical_filters = ['SDSSg_65mm~empty', 'SDSSr_65mm~empty','SDSSi_65mm~empty']
def test_for_calibration(butler, collection, calibration_type, physical_filter) :
    ## This function just tries to get a defect from the collection.
    ## If successfull it passes True, otherwise False.
    try :
        butler.get(calibration_type, instrument='LATISS', physical_filter=physical_filter, detector=0, collections=collection)
        exists = True
    except :
        exists = False
    return exists

large_flat_collection = []
for i in range(len(physical_filters)):
    flat_collections = [c for c in sorted(registry.queryCollections())  if test_for_calibration(butler, c, 'flat', physical_filters[i])]
    large_flat_collection+=flat_collections
with open('flat_test_collections.txt', 'w') as f:
    for col in large_flat_collection:
        f.write(f"{col}\n")