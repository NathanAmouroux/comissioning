import numpy as np
import lsst.daf.butler as dafButler
import sys
import configparser
import argparse

parser = argparse.ArgumentParser(description='Python script with a config file.')
parser.add_argument('-c', '--config', help='Path to the config file', required=True)
args = parser.parse_args()

config_file_path = args.config
config = configparser.ConfigParser()
config.read("/sdf/home/a/amouroux/public_html/AuxTel/config.ini")
config_settings = config['Settings']

# Access your configuration settings
key1_value = config_settings['key1']
key2_value = config_settings['key2']

# Use the configuration settings as needed
print(f'Value of key1: {key1_value}')
print(f'Value of key2: {key2_value}')

## Paths
repo = '/sdf/group/rubin/repo/embargo/butler.yaml'
base_path = sys.argv[1]
#collection = "LATISS/runs/AUXTEL_DRP_IMAGING_2023-11A-10A-09AB-08ABC-07AB-05AB/w_2023_46/PREOPS-4553"
collection = "LATISS/runs/AUXTEL_DRP_IMAGING_2023-09A-08ABC-07AB-05AB/d_2023_09_25/PREOPS-3780"
#collection = sys.argv[1]
outpath = "/sdf/data/rubin/user/amouroux/comissioning/AuxTel/calibration_collections/save_load_collections_pckgs/" + f"{collection.split('/')[-1]}"

## Load butler
butler = dafButler.Butler(repo, collections=collection)
registry = butler.registry
print("Butler successfuly instatiated")

## Useful functions
def get_chain(collection):
    chain = registry.getCollectionChain(collection)
    calibs = [c for c in sorted(chain, reverse = True) if "LATISS/calib" in c]
    return calibs

## Get chained calibrations and print them
calib_chain = get_chain(collection)
with open(outpath + '_calibrations_chained.txt', 'w') as f:
    for col in calib_chain:
        f.write(f"{col}\n")
        
print("Chained calibrations are the following :")
for c in calib_chain:
    print(c)
print("\n\n")

## Search which calibration types are avaible
c_types = np.array(["flat-i", "flat-z", "flat-y", "flat-g", "flat-r", "bias", "defects", "dark", "crosstalk"])
calib_types, calib_names = [], []

for i, element in enumerate(calib_chain):
    for calib_t in c_types:
        if calib_t in element and calib_t not in calib_types:
            print(f"Found {calib_t}.")
            calib_types.append(calib_t)
            calib_names.append(element)
        else :
            print(f"{calib_t} not found.")
with open(outpath + '_last_calibrations.txt', 'w') as f:
    for col1, col2 in np.column_stack((calib_names, calib_types)):
        f.write(f"{col1}\t{col2}\n")

## Save butler path to access found calibrations data 
datasets = []
coll_paths = []
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
with open(outpath + '_calibrations_access.txt', 'w') as f:
    for col1, col2 in np.column_stack((coll_paths, physical_filters)):
        f.write(f"{col1}\t{col2}\n")

sys.exit()