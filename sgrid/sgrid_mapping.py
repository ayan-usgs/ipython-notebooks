import bisect
import datetime
import os

import matplotlib.pyplot as plt
import netCDF4 as nc4
import numpy as np

from pysgrid import from_nc_dataset
from pysgrid.processing_2d import avg_to_cell_center, rotate_vectors, vector_sum


def nearest_time(nc_dataset, time):
    time_var = nc_dataset.variables['time']
    time_units = time_var.units
    try:
        calendar = time_var.calendar
    except AttributeError:
        calendar = 'gregorian'
    num_date = round(nc4.date2num(time, units=time_units, calendar=calendar))
    times = time_var[:]
    time_index = bisect.bisect_right(times, num_date)
    try:
        time_val = times[time_index]
    except IndexError:
        time_index -= 1
        time_val = times[time_index]
    return time_index, time_val
    
    
def lon_lat_subset_idx(lon, lat, lon_min, lat_min, lon_max, lat_max, padding=0.18):
    x = np.where((lon <= (lon_max + padding)) & (lon >= (lon_min - padding)) &
                 (lat <= (lat_max + padding)) & (lat >= (lat_min - padding))
                )
    subset_idx = np.asarray(x)
    return subset_idx
    
    
def subset_data(data, subset_indices):
    rows = subset_indices[0, :]
    columns = subset_indices[1, :]
    data_subset = data[rows, columns]
    return data_subset
    
    
def parse_variable_coordinates(variable_obj):
    var_dims = len(variable_obj.dimensions)
    var_coordinates = variable_obj.coordinates.strip().split(' ')
    if var_dims < len(var_coordinates):
        c_idx = len(var_coordinates) - var_dims
        filtered_var_coord = var_coordinates[c_idx:]
    else:
        filtered_var_coord = var_coordinates
    return filtered_var_coord
    
    
def find_depth_variable(variable_obj, nc_dataset):
    var_coordinates = parse_variable_coordinates(variable_obj)
    for var_coordinate in var_coordinates:
        var_obj = nc_dataset.variables[var_coordinate.strip()]
        if ((hasattr(var_obj, 'axis') and var_obj.axis.lower().strip() == 'z') or
            (hasattr(var_obj, 'positive') and var_obj.positive.lower().strip() in ['up', 'down'])
            ):
            depth_variable = var_coordinate
            break  # exit loop once the depth variable is found
        else:
            depth_variable = None
    return depth_variable
    

def nearest_z(variable_obj, nc_dataset, z):
    depth_variable = find_depth_variable(variable_obj, nc_dataset)
    depth_data = nc_dataset.variables[depth_variable][:]
    depth_idx = bisect.bisect_right(depth_data, z)
    try:
        depth = depth_data[depth_idx]
    except IndexError:
        depth_idx -= 1
        depth = depth_data[depth_dix]
    return depth_idx, depth
    
    
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
    LAYER = 'u,v'
    
    os.environ['TCL_LIBRARY'] = 'C:/Python279/tcl/tcl8.5'
    os.environ['TK_LIBRARY'] = 'C:/Python279/tcl/tk8.5'
    
    t = datetime.datetime(2012, 6, 25, 2, 0)
    z = -0.85
    
    cached_dataset = nc4.Dataset(CACHED_URL)
    canon_dataset = nc4.Dataset(DATASET_URL)
    
    time_idx, time_val = nearest_time(cached_dataset, t)
    print('Time value: {0}'.format(time_val))
    cached_sg = from_nc_dataset(cached_dataset)
    
    lon_name, lat_name = cached_sg.face_coordinates
    lon_obj = getattr(cached_sg, lon_name)
    lat_obj = getattr(cached_sg, lat_name)
    centers = cached_sg.centers
    longitudes = centers[..., 0][lon_obj.center_slicing]
    latitudes = centers[..., 1][lat_obj.center_slicing]
    angles = cached_sg.angles[lon_obj.center_slicing]
    # get the indices of the longitude and latitude that fall within the specified bounds
    subset_idx = lon_lat_subset_idx(longitudes, latitudes, LON_MIN, LAT_MIN, LON_MAX, LAT_MAX)
    subset_lon = subset_data(longitudes, subset_idx)
    subset_lat = subset_data(latitudes, subset_idx)
    
    layer = LAYER
    variables = layer.split(',')
    var1_name = variables[0]
    var2_name = variables[1]
    cached_var1 = getattr(cached_sg, var1_name)
    cached_var2 = getattr(cached_sg, var2_name)
    raw_var1 = canon_dataset.variables[var1_name]
    raw_var2 = canon_dataset.variables[var2_name]
    vertical_index, vertical = nearest_z(raw_var1, canon_dataset, z)
    print('Vertical: {0}'.format(vertical))
    var1_trimmed = raw_var1[time_idx, vertical_index, cached_var1.center_slicing[2], cached_var1.center_slicing[3]]
    var2_trimmed = raw_var2[time_idx, vertical_index, cached_var2.center_slicing[2], cached_var2.center_slicing[3]]
    var1_avg = avg_to_cell_center(var1_trimmed, cached_var1.center_axis)
    var2_avg = avg_to_cell_center(var2_trimmed, cached_var2.center_axis)
    if cached_var1.center_axis == 1 and cached_var2.center_axis == 0:
        x_var = var1_avg
        y_var = var2_avg
    else:
        x_var = var2_avg
        y_var = var1_avg
    x_rot, y_rot = rotate_vectors(x_var, y_var, angles)
    subset_x_rot = subset_data(x_rot, subset_idx)
    subset_y_rot = subset_data(y_rot, subset_idx)
    xy_vector_sum = vector_sum(subset_x_rot, subset_y_rot)
    
    fig = plt.figure(figsize=(12, 12))
    plt.subplot(111, aspect=(1.0/np.cos(np.mean(subset_lat)*np.pi/180.0)))
    q = plt.quiver(subset_lon[::SUB], 
                   subset_lat[::SUB], 
                   subset_x_rot[::SUB], 
                   subset_y_rot[::SUB],
                   xy_vector_sum[::SUB],
                   scale=1.0/SCALE, 
                   pivot='middle', 
                   zorder=1e35, 
                   width=0.003
                   )