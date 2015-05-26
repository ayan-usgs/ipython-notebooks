import netCDF4 as nc4

from pysgrid import from_nc_dataset


WRF_TEST_FILE = 'http://geoport.whoi.edu/thredds/dodsC/usgs/data1/rsignell/models/wrf/sgrid.ncml'

ds = nc4.Dataset(WRF_TEST_FILE)
sg = from_nc_dataset(ds)

centers = sg.centers
xlat_u = ds.variables['XLAT_U']
xlong_u = ds.variables['XLONG_U']
xlat_v = ds.variables['XLAT_V']
xlong_v = ds.variables['XLONG_V']