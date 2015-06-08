import bisect
import datetime
import os

import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation
import netCDF4 as nc4
import numpy as np
import numpy.ma as ma
import pyproj

from pysgrid import from_nc_dataset
from pysgrid.processing_2d import avg_to_cell_center, rotate_vectors, vector_sum

from sgrid_mapping import (find_depth_variable, nearest_time, 
                           nearest_z, parse_variable_coordinates,
                           lon_lat_subset_idx, subset_data)


if __name__ == '__main__':

    CACHED_URL = 'C:/Users/ayan/Desktop/tmp/sgrid1.nc'
    DATASET_URL = 'http://geoport.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd'
    SUB = 1
    SCALE = 0.06
    LON_MAX = -60.88
    LON_MIN = -80.25
    LAT_MAX = 47.05
    LAT_MIN = 12.01
    PADDING = 0.18
    LAYER = 'temp'
    
    os.environ['TCL_LIBRARY'] = 'C:/Python279/tcl/tcl8.5'
    os.environ['TK_LIBRARY'] = 'C:/Python279/tcl/tk8.5'
    
    t = datetime.datetime(2012, 6, 25, 2, 0)
    z = -0.85    
    
    EPSG4326 = pyproj.Proj('+init=EPSG:4326')
    
    cached_dataset = nc4.Dataset(CACHED_URL)
    canon_dataset = nc4.Dataset(DATASET_URL)
    
    time_idx, time_val = nearest_time(cached_dataset, t)
    cached_sg = from_nc_dataset(cached_dataset)
    
    lon_name, lat_name = cached_sg.face_coordinates
    lon_obj = getattr(cached_sg, lon_name)
    lat_obj = getattr(cached_sg, lat_name)
    mask_rho_obj = cached_sg.mask_rho
    raw_mask = canon_dataset.variables['mask_rho'][:, :]
    trimed_mask = raw_mask[mask_rho_obj.center_slicing]
    centers = cached_sg.centers
    longitudes = centers[..., 0]
    latitudes = centers[..., 1]
    lon_trim = longitudes[lon_obj.center_slicing]
    lat_trim = latitudes[lat_obj.center_slicing]
    # get the indices of the longitude and latitude that fall within the specified bounds
    subset_idx = lon_lat_subset_idx(lon_trim, lat_trim, LON_MIN, LAT_MIN, LON_MAX, LAT_MAX)
    subset_lon = subset_data(lon_trim, subset_idx)
    subset_lat = subset_data(lat_trim, subset_idx)
    
    var1_name = LAYER
    cached_var1 =  getattr(cached_sg, var1_name)
    raw_var1 = canon_dataset.variables[var1_name]
    
    vertical_index, vertical = nearest_z(raw_var1, canon_dataset, z)
    # var1_trimmed = raw_var1[time_idx, vertical_index, cached_var1.center_slicing[2], cached_var1.center_slicing[3]]
    var1_trimmed = raw_var1[-1, -1, :, :]
    subset_var1 = subset_data(var1_trimmed, subset_idx)
    
    fig = plt.figure(figsize=(12, 12), dpi=80)
    # plt.subplot(111, aspect=(1.0/np.cos(np.mean(subset_lat)*np.pi/180.0)))
    masked = ma.masked_where(1-raw_mask, var1_trimmed)
    print(masked)
    plt.pcolormesh(longitudes, latitudes, masked, vmin=5, vmax=30)