import numpy as np
import lsst.daf.butler as dafButler
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1 import make_axes_locatable
from astropy.table import Table 
import sys
import pickle
from configparser import ConfigParser

## Get configs
config = ConfigParser()
config.read("../config.ini")

## Set inpath & outpath 
collection = sys.argv[1]
inpath = config.get('auxtel', 'base_save_path') + 'save_collections/datas/' + f"{collection.split('/')[-1]}"
outpath = config.get('auxtel', 'base_save_path') + 'save_collections/figures/' + f"{collection.split('/')[-1]}"

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

with open(inpath + f"_data_calibration.pkl", 'rb') as fichier:
    calib = pickle.load(fichier)

range_dict = {"calib_type" : ["flat", "defects", "dark", "bias", "crosstalk"], "range" : [(0.9,1.1), (0,1), (-0.1,0.1), (-4,4), (0,0.0005)]} #For plotting
print(range_dict)

##First raw plot 

print("now plotting....")
n_lignes = round((len(calib["calib_type"]))/2)
fig, axs = plt.subplots(n_lignes,2, figsize=(15,20))
ax_l = [ax for ax in axs.flat]
for i in range(len(calib["calib_type"])):
    vmin, vmax = range_dict["range"][range_dict["calib_type"].index(calib['calib_type'][i].split('-')[0])]
    if calib['calib_type'][i] != "crosstalk":
        if calib['calib_type'][i] != "defects" :
            im = ax_l[i].imshow(calib['calib_data'][i], cmap='hot', vmin = vmin, vmax = vmax)
            divider = make_axes_locatable(ax_l[i])
            cax = divider.append_axes('right', size='5%', pad=0.05)
            fig.colorbar(im, cax=cax, orientation='vertical')
        elif calib['calib_type'][i] == "defects":
            print("defects!")
            _ = make_error_boxes(ax_l[i], calib['calib_data'][i]['x0'], calib['calib_data'][i]['y0'], calib['calib_data'][i]['width'], calib['calib_data'][i]['height'])
            [ax_l[i].axhline(l, lw=0.1, c='k') for l in np.linspace(0,4000,3)]
            [ax_l[i].axvline(l, lw=0.1, c='k') for l in np.linspace(0,4000,9)]
        ax_l[i].set_xlim(-10,4010)
        ax_l[i].set_ylim(-10,4010)
        ax_l[i].set_aspect('equal')
        ax_l[i].set_title(calib['calib_type'][i])
    elif calib['calib_type'][i] == "crosstalk":
        print("crosstalk!")
        im = ax_l[i].imshow(calib['calib_data'][i], vmin = vmin, vmax = vmax)
        ax_l[i].set_title('crosstalk')
        divider = make_axes_locatable(ax_l[i])
        cax = divider.append_axes('right', size='5%', pad=0.05)
        amp_l = [f"C0{i}" for i in range(8)] + [f"C1{i}" for i in range(8)]
        ticks = [i for i in range(16)]
        ax_l[i].set_xticks(ticks = ticks, labels = amp_l, fontsize = 9)
        ax_l[i].set_yticks(ticks = ticks, labels = amp_l, fontsize = 9)
        ax_l[i].set_xlabel("Victim amplifier")
        ax_l[i].set_ylabel("Source amplifier")
        fig.colorbar(im, cax=cax, orientation='vertical')
if len(calib["calib_type"])%2 !=0:
    fig.delaxes(ax_l[-1])
fig.suptitle(collection, fontsize = 16)
#fig.subplots_adjust(hspace=0.50)
fig.tight_layout()
fig.subplots_adjust(top=0.94)
plt.savefig(outpath + f"_calibration_data_plots.png", bbox_inches='tight')
plt.close()

sys.exit()