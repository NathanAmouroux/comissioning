import sys
sys.path.append('/sdf/data/rubin/user/amouroux/comissioning/module_calibration_collections/vizualize_calibrations')
import vizualize_calib
#collections = ['LATISS/runs/AUXTEL_DRP_IMAGING_20230509_20231207/w_2023_49/PREOPS-4648', 'u/huanlin/LATISS/runs/AUXTEL_DRP_IMAGING_2023-11A-10A-09AB-08ABC-07AB-05AB/w_2023_47/DM-39038', 'LATISS/runs/AUXTEL_DRP_IMAGING_2023-11A-10A-09AB-08ABC-07AB-05AB/w_2023_46/PREOPS-4553']
collections = 'LATISS/runs/AUXTEL_DRP_IMAGING_20230509_20240201/w_2024_05/PREOPS-4871'
#get_viz = vizualize_calib.vizualize(collection = "LSSTComCam/calib", exp="LSSTComCam", calib = "flat-i")
#get_viz.plot_calib_lot(collection = "LSSTComCam/calib", exp = "LSSTComCam", is_chained = False, detector = 1)
get_viz = vizualize_calib.vizualize(collection = collections)
get_viz.plot_calib_lot(collection = collections)