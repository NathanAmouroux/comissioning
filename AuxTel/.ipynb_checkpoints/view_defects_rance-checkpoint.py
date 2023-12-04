import numpy as np
#from lsst.daf.butler import Butler
import lsst.daf.butler as dafButler
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle

def test_for_defects(butler, collection) :
    ## This function just tries to get a defect from the collection.
    ## If successfull it passes True, otherwise False.
    try :
        butler.get('defects', instrument='LATISS', detector=0, collections=collection)
        exists = True
    except :
        exists = False
    return exists


def make_error_boxes(ax, xdata, ydata, xerror, yerror, facecolor='k', edgecolor='none', alpha=1):
    ## This function just draws in boxes in the shapes of the defects.

    # Loop over data points; create box from errors at each point
    errorboxes = [Rectangle((x, y), xe, ye, rotation_point='center')
                  for x, y, xe, ye in zip(xdata, ydata, xerror, yerror)]

    # Create patch collection with specified colour/alpha
    pc = PatchCollection(errorboxes, facecolor=facecolor, alpha=alpha,
                         edgecolor=edgecolor)

    # Add collection to axes
    ax.add_collection(pc)

    # Plot errorbars
    artists = ax.errorbar(xdata+0.5*xerror, ydata+0.5*yerror, xerr=0.5*xerror, yerr=0.5*yerror,
                          fmt='none', ecolor='k')

    return artists



repo = '/sps/lsst/groups/auxtel/softs/shared/auxteldm_gen3/data/'

## GET THE COLLECTIONS THAT HAVE DEFECTS
#registry = Butler.registry
#defect_collections = [c for c in sorted(registry.queryCollections()) if test_for_defects(butler, c)]

#with open('defect_collections.txt', 'w') as f:
#    for col in defect_collections :
#        f.write(f"{col}\n")


## NOW VIEW ONE OF THE DEFECTS
collection = 'u/plazas/DM-38563.combined.defects.type_VALUE.hot_3.cold_0.9.2023OCT04.2/20231005T022801Z'

butler = dafButler.Butler(repo, collections=collection)
defect_ = butler.get('defects', instrument='LATISS', detector=0, collections=collection)
print(defect_)
defect = defect_.toTable()[0]
print(defect)
plt.figure()
#figsize = (3.5,3.5)
fig, ax = plt.subplots(1,1)#, figsize=figsize)
_ = make_error_boxes(ax, defect['x0'], defect['y0'], defect['width'], defect['height'])
[ax.axhline(l, lw=0.1, c='k') for l in np.linspace(0,4000,3)]
[ax.axvline(l, lw=0.1, c='k') for l in np.linspace(0,4000,9)]
ax.set_xlim(-10,4010)
ax.set_ylim(-10,4010)
ax.set_aspect('equal')
ax.set_xlabel('x')
ax.set_ylabel('y')
#plt.show()
plt.savefig('/sps/lsst/users/tguillem/web/debug/defects_stack/defects.png')
#plt.close()

#plt.figure()
#plt.imshow(defectArray_copy, origin='lower', vmin=0, vmax=1, cmap='tab10') #cmap='tab10' / cmap=cmapmine
##bug
##plt.imshow(defectArray_copy, origin='lower', vmin=0, vmax=1, cmap=cmapmine)# interpolation='none') #extent=[0,4072,0,100])
#plt.colorbar()
#p#lt.title(collection[0]+'\n'+ detector_name)
#p#lt.savefig(outpath_raft+'image_'+ccds[i_ccd]+'.png')
#plt.close()
