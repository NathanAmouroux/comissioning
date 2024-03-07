import numpy as np
import lsst.daf.butler as dafButler
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pickle
from configparser import ConfigParser
################NEED TO INCLUDE OUTPUT OF THIS IN VIZUALIZE_CALIBS AND DO ANOTHER VIZUALIZE_DUAL
## Get configs
config = ConfigParser()
config.read("../config.ini")

## Set inpath & outpath 
collections = [sys.argv[1], sys.argv[2]]
inpaths = [config.get('auxtel', 'base_save_path') + 'save_collections/datas/' + f"{collections[i].split('/')[-1]}" for i in range(2)]

outpath = config.get('auxtel', 'base_save_path') + 'save_collections/figures/' + f"{collections[0].split('/')[-1]}_vs_{collections[1].split('/')[-1]}"

calibs = []
for i in range(2):
    with open(inpaths[i] + f"_data_calibration.pkl", 'rb') as fichier:
        calibs.append(pickle.load(fichier))

calib_diff = {"calib_type":[],"calib_data":[]}
if len(calibs[0]["calib_type"]) > len(calibs[1]["calib_type"]):
    n_var_max = len(calibs[0]["calib_type"])
    ref_cal = calibs[0]["calib_type"]
    print(ref_cal, calibs[1]["calib_type"])
elif len(calibs[0]["calib_type"]) < len(calibs[1]["calib_type"]):
    n_var_max = len(calibs[1]["calib_type"])
    ref_cal = calibs[1]["calib_type"]
    print(ref_cal, calibs[0]["calib_type"])
else : 
    n_var_max = len(calibs[0]["calib_type"])
    ref_cal = calibs[0]["calib_type"]
    
for type in ref_cal:
    if type in calibs[0]["calib_type"] and type in calibs[1]["calib_type"] :
        calib_diff["calib_type"].append(type)
    else :
        print(f"{type} not in both calibration collections")
    
for type in calib_diff["calib_type"]:
    calib1 = calibs[0]["calib_data"][np.where(calibs[0]["calib_type"]==type)[0][0]]
    calib2 = calibs[1]["calib_data"][np.where(calibs[1]["calib_type"]==type)[0][0]]
    if type!="defects":
        diff = calib1-calib2
    else:
        diff = [calib1, calib2]
    calib_diff["calib_data"].append(diff)

range_dict = {"calib_type" : ["flat", "defects", "dark", "bias", "crosstalk"], "range" : [(0.9,1.1), (0,1), (-0.1,0.1), (-4,4), (0,0.0005)]}
print(range_dict)
##First diff plot 

print("now plotting raw diff....")
n_lignes = len(calib_diff["calib_type"])
fig, axs = plt.subplots(n_lignes,2, figsize=(15,30))
ax_l = [ax for ax in axs.flat]
for i in range(len(calib_diff["calib_type"])):
    vmin, vmax = range_dict["range"][range_dict["calib_type"].index(calib_diff['calib_type'][i].split('-')[0])]
    for j in range(2):
        if calib_diff['calib_type'][i] != "crosstalk":
            if calib_diff['calib_type'][i] != "defects" :
                im = axs[i][j].imshow(calib_diff[j]['calib_data'][i], cmap='hot', vmin = vmin, vmax = vmax)
                divider = make_axes_locatable(axs[i][j])
                cax = divider.append_axes('right', size='5%', pad=0.05)
                fig.colorbar(im, cax=cax, orientation='vertical')
            else :
                print("defects!")
                _ = make_error_boxes(axs[i][j], calib[j]['calib_data'][i]['x0'], calib[j]['calib_data'][i]['y0'], calib[j]['calib_data'][i]['width'], calib[j]['calib_data'][i]['height'])
                [axs[i][j].axhline(l, lw=0.1, c='k') for l in np.linspace(0,4000,3)]
                [axs[i][j].axvline(l, lw=0.1, c='k') for l in np.linspace(0,4000,9)]
            axs[i][j].set_xlim(-10,4010)
            axs[i][j].set_ylim(-10,4010)
            axs[i][j].set_aspect('equal')
            axs[i][j].set_title(calib['calib_type'][i])
        else:
            print("crosstalk!")
            im = axs[i][j].imshow(calib_diff[j]['calib_data'][i], vmin = vmin, vmax = vmax)
            axs[i][j].set_title('crosstalk')
            divider = make_axes_locatable(axs[i][j])
            cax = divider.append_axes('right', size='5%', pad=0.05)
            amp_l = [f"C0{i}" for i in range(8)] + [f"C1{i}" for i in range(8)]
            ticks = [i for i in range(16)]
            axs[i][j].set_xticks(ticks = ticks, labels = amp_l, fontsize = 9)
            axs[i][j].set_yticks(ticks = ticks, labels = amp_l, fontsize = 9)
            axs[i][j].set_xlabel("Victim amplifier")
            axs[i][j].set_ylabel("Source amplifier")
            fig.colorbar(im, cax=cax, orientation='vertical')
fig.suptitle((collections[0].split('/')[-1] + collections[1].split('/')[-1]), fontsize = 16)
#fig.subplots_adjust(hspace=0.50)
fig.tight_layout()
fig.subplots_adjust(top=0.94)
plt.savefig(f"{collections[0].split('/')[-1]}" + "_vs_" + f"{collections[1].split('/')[-1]}_calibration_data_plots.png", bbox_inches='tight')



plt.close()
sys.exit()
