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

#collection = "LATISS/runs/AUXTEL_DRP_IMAGING_2023-11A-10A-09AB-08ABC-07AB-05AB/w_2023_46/PREOPS-4553"
collection = "LATISS/runs/AUXTEL_DRP_IMAGING_2023-09A-08ABC-07AB-05AB/d_2023_09_25/PREOPS-3780"
#collection = sys.argv[1]
inpath = "/sdf/home/a/amouroux/rubin-user/comissioning/AuxTel/calibration_collections/save_load_collections_pckgs/"
outpath = "/sdf/home/a/amouroux/rubin-user/comissioning/AuxTel/calibration_collections/vizualize_calibs/"
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

with open(inpath + f"{collection.split('/')[-1]}_data_calibration.pkl", 'rb') as fichier:
    calib = pickle.load(fichier)

range_dict = {"calib_type" : ["flat", "defects", "dark", "bias", "crosstalk"], "range" : [(0.9,1.1), (0,1), (-0.1,0.1), (-4,4), (0,0.0005)]}
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
    
"""
im1 = ax1.imshow(1-calib[0], cmap='hot')
ax1.set_title('Defects')
divider = make_axes_locatable(ax1)
cax = divider.append_axes('right', size='5%', pad=0.05)
fig.colorbar(im1, cax=cax, orientation='vertical')

im2 = ax2.imshow(calib[1], vmax=4, vmin=-4, cmap='hot')
ax2.set_title('Bias')
divider = make_axes_locatable(ax2)
cax = divider.append_axes('right', size='5%', pad=0.05)
fig.colorbar(im2, cax=cax, orientation='vertical')
#plt.colorbar(plot2, cax=ax2)

im3 = ax3.imshow(calib[2], vmax=1.1, vmin=0.9, cmap='hot')
ax3.set_title('flat')
divider = make_axes_locatable(ax3)
cax = divider.append_axes('right', size='5%', pad=0.05)
fig.colorbar(im3, cax=cax, orientation='vertical')

im4 = ax4.imshow(calib[3], vmax=.01, vmin=-0.01, cmap='hot')
ax4.set_title('Dark')
divider = make_axes_locatable(ax4)
cax = divider.append_axes('right', size='5%', pad=0.05)
fig.colorbar(im4, cax=cax, orientation='vertical')

im5 = ax5.imshow(calib[4], vmax = 0.0005, vmin=0)
ax5.set_title('crosstalk')
divider = make_axes_locatable(ax5)
cax = divider.append_axes('right', size='5%', pad=0.05)
"""

plt.savefig(outpath + f"{collection.split('/')[-1]}_calibration_data_plots.png", bbox_inches='tight')
plt.close()
sys.exit()