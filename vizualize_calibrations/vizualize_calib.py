import numpy as np
import lsst.daf.butler as dafButler
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1 import make_axes_locatable
from astropy.table import Table 
import sys
import os
import pickle
from configparser import ConfigParser
sys.path.append('/sdf/data/rubin/user/amouroux/comissioning/module_calibration_collections/save_calibrations_data')
import save_dataset

class vizualize:
    def __init__(self, collection=None, detector = 0, repo = 'embargo', exp = 'LATISS', is_chained = True):
        self.config = ConfigParser()
        self.config.read("/sdf/data/rubin/user/amouroux/comissioning/module_calibration_collections/config.ini")
        self.repo = self.config.get('base', repo + '_repo')
        self.detector = detector
        self.collection = collection
        self.exp = exp
        self.is_chained = is_chained
        #self.outpath = config.get(self.exp, 'base_save_path') + 'saved_collections/paths/' + f"{self.collection.split('/')[-1]}"

    def open_calib(self, calib, inpath = None):
        if inpath == None:
            inpath = self.config.get(self.exp, 'base_save_path') + 'saved_collections/datas/' + f"{self.collection.split('/')[-1]}/"
        if os.path.exists(self.config.get(self.exp, 'base_save_path') + 'saved_collections/datas/' + f"{self.collection.split('/')[-1]}/{calib}_{self.detector}_data.pkl"):
            inpath = self.config.get(self.exp, 'base_save_path') + 'saved_collections/datas/' + f"{self.collection.split('/')[-1]}/{calib}_{self.detector}_data.pkl"
            with open(inpath, 'rb') as file:
                calib_arr = pickle.load(file)
        else : 
            datas = save_dataset.Data(collection=self.collection, exp=self.exp, calib=calib, is_chained=self.is_chained, detector=self.detector)
            calib_arr = datas.save_calibration_data(outpath = inpath)
        return calib_arr

    def make_error_boxes(self, ax, xdata, ydata, xerror, yerror, facecolor='k', edgecolor='none', alpha=1):
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

    def plot_array(self, data, vmin, vmax, calib, fig, ax):
        im = ax.imshow(data, cmap = 'hot', vmin = vmin, vmax = vmax)
        ax.set_xlim(0,4070)
        ax.set_ylim(0,4000)
        ax.set_aspect('equal')
        fig.colorbar(im, ax=ax, orientation='vertical', fraction=0.046, pad=0.04)
        ax.set_title(calib, fontsize = 13)
        return fig
    
    def plot_defects(self, data, fig, ax):
        im = self.make_error_boxes(ax, data['x0'], data['y0'], data['width'], data['height'])
        [ax.axhline(l, lw=0.1, c='k') for l in np.linspace(0,4000,3)]
        [ax.axvline(l, lw=0.1, c='k') for l in np.linspace(0,4070,9)]
        ax.set_xlim(0,4070)
        ax.set_ylim(0,4000)
        ax.set_aspect('equal')
        ax.set_title("defects", fontsize = 13)
        return fig
    
    def plot_crosstalk(self, data, vmin, vmax, fig, ax):
        im = ax.imshow(data, vmin = vmin, vmax = vmax)
        ax.set_title('crosstalk', fontsize = 13)
        amp_l = [f"C0{i}" for i in range(8)] + [f"C1{i}" for i in range(8)]
        ticks = [i for i in range(16)]
        ax.set_xticks(ticks = ticks, labels = amp_l, fontsize = 9)
        ax.set_yticks(ticks = ticks, labels = amp_l, fontsize = 9)
        ax.set_xlabel("Victim amplifier")
        ax.set_ylabel("Source amplifier")
        fig.colorbar(im, ax=ax, orientation='vertical', fraction=0.046, pad=0.04)
        return fig
    
    def plot_calib(self, calib, range = None, fig = None, ax = None, inpath = None, savefig = True, outpath = None):
        calib_arr = self.open_calib(calib=calib, inpath = inpath)
        if ax is None : 
            fig, ax = plt.subplots(figsize = (7,7))
        if range is None :
            range_dict = {"calib_type" : ["flat", "defects", "dark", "bias", "crosstalk"], "range" : [(0.9,1.1), (0,1), (-0.1,0.1), (-4,4), (0,0.0005)]} #For plotting
            vmin, vmax = range_dict["range"][range_dict["calib_type"].index(calib.split('-')[0])]
        else :
            vmin, vmax = range
        if calib.split("-")[0] == "flat" or calib == "dark" or calib == "bias":
            figure = self.plot_array(calib_arr, vmin, vmax, calib, fig, ax)
        elif calib == "defects":
            figure = self.plot_defects(calib_arr, fig, ax)
        elif calib == "crosstalk":
            figure = self.plot_crosstalk(calib_arr, vmin, vmax, fig, ax)
        if savefig == True:
            if outpath is None : 
                if not os.path.exists(self.config.get(self.exp, 'base_save_path') + 'saved_collections/figures/' + f"{self.collection.split('/')[-1]}/"):
                    os.mkdir(self.config.get(self.exp, 'base_save_path') + 'saved_collections/figures/' + f"{self.collection.split('/')[-1]}/")
                outpath = self.config.get(self.exp, 'base_save_path') + 'saved_collections/figures/' + f"{self.collection.split('/')[-1]}/"
            figure.savefig(outpath + f"{calib}_{self.detector}_plot.png", bbox_inches='tight')
        return figure

    def plot_multiple_calibs(self, calibs, range = None, inpath = None, savefig = True, outpath = None):
        n_lines = round(len(calibs)/2)
        fig, axs = plt.subplots(n_lines,2,figsize=(15,7*n_lines))
        ax_l = [ax for ax in axs.flat]
        if range == None:
            range_dict = {"calib_type" : ["flat", "defects", "dark", "bias", "crosstalk"], "range" : [(0.9,1.1), (0,1), (-0.1,0.1), (-4,4), (0,0.0005)]}
            range = [range_dict["range"][range_dict["calib_type"].index(calib.split('-')[0])] for calib in calibs]
        count, calib_found = 0, []
        for i, calib in enumerate(calibs):   #Plot multiple calibs on same figure
            vmin, vmax = range[i][0], range[i][1]
            try :
                figure = self.plot_calib(calib, range=(vmin,vmax),fig = fig, ax=ax_l[i-count], inpath=inpath, savefig = False, outpath=outpath)
                calib_found.append(calib)
            except:
                print(f"Exception encountered, {calib} not found.") 
                count += 1
                figure.delaxes(ax_l[-1*count])
        if outpath == None : 
            if not os.path.exists(self.config.get(self.exp, 'base_save_path') + 'saved_collections/figures/' + f"{self.collection.split('/')[-1]}/"):
                os.mkdir(self.config.get(self.exp, 'base_save_path') + 'saved_collections/figures/' + f"{self.collection.split('/')[-1]}/")
            outpath = self.config.get(self.exp, 'base_save_path') + 'saved_collections/figures/' + f"{self.collection.split('/')[-1]}/"
        if len(calibs)%2 !=0:
            figure.delaxes(ax_l[-1-count])
        fig.suptitle(self.collection, fontsize = 16)
        #fig.subplots_adjust(hspace=0.50)
        fig.tight_layout()
        fig.subplots_adjust(top=0.95)
        if len(calib_found)>=5:
            calib_found = "lot"
        fig.savefig(outpath + f"{calib_found}_{self.detector}_plot.png", bbox_inches='tight')    
        return fig
        
    def plot_calib_lot(self, range = None, inpath = None, savefig = True, outpath = None):
        calibs = ["flat-i", "flat-z", "flat-y", "flat-g", "flat-r", "flat-u", "bias", "defects", "dark", "crosstalk"]
        fig = self.plot_multiple_calibs(calibs = calibs, range = range, inpath = inpath, savefig = savefig, outpath = outpath)

"""
Not finished, still to implement raft vizualisation"""
        
"""
    def plot_calib_lot #plot all of a lot on the same figure
    def assemble #When you deal with several ccd/raft
##First raw plot 

print("now plotting....")
n_lignes = round((len(calib["calib_type"]))/2)
fig, axs = plt.subplots(n_lignes,2, figsize=(15,20))
ax_l = 
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
"""