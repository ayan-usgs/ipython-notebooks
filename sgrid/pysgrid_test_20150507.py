import os

import matplotlib.pyplot as plt
import netCDF4 as nc4
import numpy as np

from pysgrid import from_nc_dataset
from pysgrid.processing_2d import avg_to_cell_center, rotate_vectors, vector_sum


os.environ['TCL_LIBRARY'] = 'C:/Python279/tcl/tcl8.5'
os.environ['TK_LIBRARY'] = 'C:/Python279/tcl/tk8.5'

DATASET_URL = 'http://geoport.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd'
TIME_INDEX = -1
VERTICAL_INDEX = -1
SUB = 1
SCALE = 0.06

ds = nc4.Dataset(DATASET_URL)

s = from_nc_dataset(ds) 
u_var = s.u
v_var = s.v
u_velocity = ds.variables['u']
v_velocity = ds.variables['v']
u_data = u_velocity[TIME_INDEX, VERTICAL_INDEX, u_var.center_slicing[2], u_var.center_slicing[3]]
v_data = v_velocity[TIME_INDEX, VERTICAL_INDEX, v_var.center_slicing[2], v_var.center_slicing[3]]
angle_var = s.angle
angle_data = s.angles
angle_data_trimed = angle_data[angle_var.center_slicing]

u_avg = avg_to_cell_center(u_data, u_var.center_axis)
v_avg = avg_to_cell_center(v_data, v_var.center_axis)

u_rot, v_rot = rotate_vectors(u_avg, v_avg, angle_data_trimed)
uv_vector_sum = vector_sum(u_rot, v_rot)

cell_centers = s.centers
lon_var, lat_var = s.face_coordinates
lon_obj = getattr(s, lon_var)
lat_obj = getattr(s, lat_var)
lon_data = cell_centers[:, :, 0]
lat_data = cell_centers[:, :, 1]
lon_subset = lon_data[lon_obj.center_slicing]
lat_subset = lat_data[lat_obj.center_slicing]

fig = plt.figure(figsize=(12, 12))
plt.subplot(111, aspect=(1.0/np.cos(np.mean(lat_subset)*np.pi/180.0)))
q = plt.quiver(lon_subset[::SUB, ::SUB], 
               lat_subset[::SUB, ::SUB], 
               u_rot[::SUB, ::SUB], 
               v_rot[::SUB, ::SUB],
               uv_vector_sum[::SUB, ::SUB],
               scale=1.0/SCALE, 
               pivot='middle', 
               zorder=1e35, 
               width=0.003
              )