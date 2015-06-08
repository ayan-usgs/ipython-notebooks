import netCDF4
import matplotlib.pyplot as plt
import numpy.ma as ma
import os


os.environ['TCL_LIBRARY'] = 'C:/Python279/tcl/tcl8.5'
os.environ['TK_LIBRARY'] = 'C:/Python279/tcl/tk8.5'


url = 'http://geoport.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd'


nc = netCDF4.Dataset(url)
ncv = nc.variables
lon = ncv['lon_rho'][:,:]
lat = ncv['lat_rho'][:,:]
rmask = 1 - ncv['mask_rho'][:,:]
t = ncv['temp'][-1,-1,:,:]
plt.pcolormesh(lon,lat,ma.masked_where(rmask,t),vmin=5,vmax=30)