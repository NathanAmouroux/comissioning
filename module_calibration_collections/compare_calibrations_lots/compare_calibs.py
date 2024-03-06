import numpy as np
import lsst.daf.butler as dafButler
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pickle
import sys

collections = ["LATISS/runs/AUXTEL_DRP_IMAGING_2023-11A-10A-09AB-08ABC-07AB-05AB/w_2023_46/PREOPS-4553", "LATISS/runs/AUXTEL_DRP_IMAGING_2023-09A-08ABC-07AB-05AB/d_2023_09_25/PREOPS-3780"]
 
class comparison:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("/sdf/data/rubin/user/amouroux/comissioning/module_calibration_collections/config.ini")
        self.repo = self.config.get('base', repo + '_repo')

    def open_calib(self, collection, exp, calib, is_chained, detector, inpath = None):
        if inpath == None:
            inpath = self.config.get(self.exp, 'base_save_path') + 'saved_collections/datas/' + f"{self.collection.split('/')[-1]}/"
        if os.path.exists(inpath + f"{calib}_{detector}_data.pkl"):
            inpath += f"{calib}_{detector}_data.pkl"
            with open(inpath, 'rb') as file:
                calib_arr = pickle.load(file)
        else : 
            datas = save_datasets.datas()
            calib_arr = datas.save_calibration_data(collection, exp, calib, is_chained, detector, outpath = inpath)
        return calib_arr
        
        
    def ccd_to_amps(self, data):
        amps = []
        x_size, y_size = 509, 2000
        for i in range(2):
            for j in range(8):
                amps.append(data[i*y_size:(i+1)*y_size,j*x_size:(j+1)*x_size])
        amps = np.array(amps)
        return amps

    def amps_to_ccd(self, data):
        ccd = np.zeros((4000,4072))
        for i in range(2):#=16
            for j in range(8):
                ccd[i*2000:(i+1)*y_size, j*x_size:(j+1)*x_size] = amps_value[(i+1)*j]
        return ccd
    
    def mean(self, data): #Used for meaning inside amp
        mean = np.zeros(len(data))
        for i in range(len(data)):
            mean[i] = np.mean(data[i])
        return mean
    
    def image_mean_by_amp(self, data):
        amps = self.ccd_to_amps(data)
        mean = self.mean(amps)
        return mean

    def difference(self, data1, data2):
        mean1, mean2 = self.image_mean_by_amp(data1), self.image_mean_by_amp(data2)
        diff = mean1 - mean2
        return diff
    def product(self, data1, data2):
        mean1, mean2 = self.image_mean_by_amp(data1), self.image_mean_by_amp(data2)
        prod =  mean1 * mean2
        return prod
    def division(self, data1, data2):
        mean1, mean2 = self.image_mean_by_amp(data1), self.image_mean_by_amp(data2)
        div = mean1/mean2
        return div
    def relative_difference(self, data1, data2):
        diff = self.difference(data1, data2)
        diff_r = diff/self.image_mean_by_amp(data1)
        return diff_r

    def save_ops(self, collections, exp, calibs, is_chained=True, detector=0, operations="difference", inpath = None, save = True): #operation must be a list
        ops : {"calib" = [], "operation" = [], "data"=[]}        
        for i, calib in enumerate(calibs):
            data = []
            count=0
            for collection in range(collections):   
                try:
                    curr_data = self.open_calib(collection, exp, calib, is_chained, detector, inpath = inpath)
                    data.append(curr_data)
                except:
                    print(f"{calib} doesn't exist in coll {collection}.")
                    count += 1
            if count==0:    
                data1, data2 = data
                ops["calib"].append(calib)
                ops["operation"].append(operations[i])
                if operations[i] == "difference":
                    ops["data"].append(self.difference(data1, data2))
                elif operations[i] == "product":
                    ops["data"].append(self.product(data1, data2))
                elif operations[i] == "division":
                    ops["data"].append(self.division(data1, data2))
                elif operations[i] == "relative_difference":
                    ops["data"].append(self.relative_difference(data1, data2))
                if save == True:
                    outpath = self.config.get(self.exp, 'base_save_path') + 'compared_collections/datas/' + f"{self.collections[0].split('/')[-1]}-{self.collections[1].split('/')[-1]}/"
                    if not os.path.exists(outpath):
                        os.mkdir(outpath)
                    with open(outpath+f"{calib}_{detector}_{operations[i]}_data.pkl", 'wb') as file:
                        pickle.dump(ops, file)
        return ops

    

"""    
inpath = "/sdf/home/a/amouroux/rubin-user/comissioning/AuxTel/calibration_collections/save_load_collections_pckgs/"
calibs = []
for i in range(2):
    with open(inpath + f"{collections[i].split('/')[-1]}_data_calibration.pkl", 'rb') as fichier:
        calibs.append(pickle.load(fichier))

calib_diff = {"calib_type":[],"calib_data_diff":[], "calib_data_frac":[]}
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
    if type!="defects" and type!="crosstalk":
        if type !="crosstalk":
            calib1 = mean(ccd_to_amps(calib1))
            calib2 = mean(ccd_to_amps(calib2))
        diff = calib1-calib2
        frac = calib1/calib2
        diff = amps_to_ccd(diff)
        frac = amps_to_ccd(frac)
    else:
        diff = [calib1, calib2]
        frac = [calib1, calib2]
    calib_diff["calib_data_diff"].append(diff)
    calib_diff["calib_data_frac"].append(frac)
    
#range_dict = {"calib_type" : ["flat", "defects", "dark", "bias", "crosstalk"], "range" : [(0.9,1.1), (0,1), (-0.1,0.1), (-4,4), (0,0.0005)]}
#range_dict = {"calib_type" : ["flat", "defects", "dark", "bias", "crosstalk"], "range" : [(-.01,.01), (0.9,1.1)]}
range_dict = {"calib_type" : ["flat-i", "flat-r", "flat-g", "defects", "dark", "bias", "crosstalk"], "range" : [(-.05,.05), (-0.005,0.005), (-0.005,0.005), (0,0), (-0.05,0.05), (-0.015,0.015), (0,0)]}
print(range_dict)
##First diff plot 

print("now plotting amp diff and frac....")
n_lignes = len(calib_diff["calib_type"])

ops = ["calib_data_diff", "calib_data_frac"]

fig, axs = plt.subplots(n_lignes-1,2, figsize=(15,30))
ax_l = [ax for ax in axs.flat]
for j, operation in enumerate(ops): #For diff + frac
    for i in range(len(calib_diff["calib_type"])):
        #vmin, vmax = range_dict["range"][j][range_dict["calib_type"].index(calib_diff['calib_type'][i].split('-')[0])]
        #vmin, vmax = range_dict["range"][j]
        vmin, vmax = range_dict["range"][range_dict["calib_type"].index(calib_diff['calib_type'][i])]
        if calib_diff['calib_type'][i] != "crosstalk":
            if calib_diff['calib_type'][i] != "defects" :
                im = axs[i][j].imshow(calib_diff[operation][i], cmap='hot', vmin = vmin, vmax = vmax)
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
            axs[i][j].set_title(calib_diff['calib_type'][i])
        else:
            print("crosstalk!")
            """
"""            im = axs[i][j].imshow(calib_diff[operation][j][i], vmin = vmin, vmax = vmax)
            axs[i][j].set_title('crosstalk')
            divider = make_axes_locatable(axs[i][j])
            cax = divider.append_axes('right', size='5%', pad=0.05)
            amp_l = [f"C0{i}" for i in range(8)] + [f"C1{i}" for i in range(8)]
            ticks = [i for i in range(16)]
            axs[i][j].set_xticks(ticks = ticks, labels = amp_l, fontsize = 9)
            axs[i][j].set_yticks(ticks = ticks, labels = amp_l, fontsize = 9)
            axs[i][j].set_xlabel("Victim amplifier")
            axs[i][j].set_ylabel("Source amplifier")
            fig.colorbar(im, cax=cax, orientation='vertical')"""
            """
fig.suptitle((collections[0].split('/')[-1] + "_vs_" + collections[1].split('/')[-1]), fontsize = 16)
#fig.subplots_adjust(hspace=0.50)
fig.tight_layout()
fig.subplots_adjust(top=0.94)
plt.savefig(f"{collections[0].split('/')[-1]}" + "_vs_" + f"{collections[1].split('/')[-1]}_calibration_data__diff_frac_plots.png", bbox_inches='tight')
plt.close()
sys.exit()
"""