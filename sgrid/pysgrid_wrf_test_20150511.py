import os

import matplotlib.pyplot as plt
import netCDF4 as nc4
import numpy as np

from pysgrid import from_nc_dataset
from pysgrid.processing_2d import avg_to_cell_center, rotate_vectors, vector_sum


WRF_TEST_FILE = 'http://geoport.whoi.edu/thredds/dodsC/usgs/data1/rsignell/models/wrf/sgrid.ncml'
VERTICAL_INDEX = 0
TIME_INDEX = 0
SUB = 1
SCALE = 0.001

os.environ['TCL_LIBRARY'] = 'C:/Python279/tcl/tcl8.5'  # windows sillyness....
os.environ['TK_LIBRARY'] = 'C:/Python279/tcl/tk8.5'
ds = nc4.Dataset(WRF_TEST_FILE)
sg = from_nc_dataset(ds)

u_var = ds.variables['U']
v_var = ds.variables['V']
sg_u = sg.U
sg_v = sg.V
u_data_trimmed = u_var[TIME_INDEX, VERTICAL_INDEX, sg_u.center_slicing[2], sg_u.center_slicing[3]]
v_data_trimmed = v_var[TIME_INDEX, VERTICAL_INDEX, sg_v.center_slicing[2], sg_v.center_slicing[3]]
u_data_avg = avg_to_cell_center(u_data_trimmed, sg_u.center_axis)
v_data_avg = avg_to_cell_center(v_data_trimmed, sg_v.center_axis)
u_rotated, v_rotated = rotate_vectors(u_data_avg, v_data_avg, sg.angles)
uv_vector_sum = vector_sum(u_rotated, v_rotated)

cell_centers = sg.centers
lon_var_name, lat_var_name = sg.face_coordinates
lon_data = cell_centers[:, :, 0]
lat_data = cell_centers[:, :, 1]
lon_var_obj = getattr(sg, lon_var_name)
lat_var_obj = getattr(sg, lat_var_name)
lon_subset = lon_data[lon_var_obj.center_slicing]
lat_subset = lat_data[lat_var_obj.center_slicing]


fig = plt.figure(figsize=(12, 12))
plt.subplot(111, aspect=(1.0/np.cos(np.mean(lat_subset)*np.pi/180.0)))
q = plt.quiver(lon_subset[::SUB, ::SUB], 
               lat_subset[::SUB, ::SUB], 
               u_rotated[::SUB, ::SUB], 
               v_rotated[::SUB, ::SUB],
               uv_vector_sum[::SUB, ::SUB],
               scale=1.0/SCALE, 
               pivot='middle', 
               zorder=1e35, 
               width=0.003
              )
