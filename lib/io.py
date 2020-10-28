#!/usr/bin/env python
# coding: utf-8

'''
    I/O utilities
'''

from netCDF4 import Dataset
import numpy as np

def loader(fname, 
    varname, 
    lon='longitude', 
    lat='latitude',
    time='time'):
    '''
    reads data from netCDF file available from SEANOE
    '''
    with Dataset(fname, 'r') as nc:
        longitudes = nc.variables[lon][:]
        latitudes = nc.variables[lat][:]
        dates = nc.variables[time][:]
        sla = nc.variables[varname][:]
    return longitudes, latitudes, dates, sla.filled(np.nan)

def writer(fname, 
    lon, 
    lat, 
    time, 
    d2d, 
    d4d):
    ''' write the output to a NetCDF file '''
    with Dataset(fname, 'w') as nc:
        
        # create dimensions
        dx = nc.createDimension('x', size=len(lon))
        dy = nc.createDimension('y', size=len(lat))
        dt = nc.createDimension('t', size=len(time))
        
        # lat/lon
        vx = nc.createVariable('longitude', 'f', dimensions=('x'))
        vx.unit = 'degrees_east'
        vx[:] = lon
        
        vy = nc.createVariable('latitude', 'f', dimensions=('y'))
        vy.unit = 'degrees_north'
        vy[:] = lat
        
        vt = nc.createVariable('time', 'f', dimensions=('t'))
        vt.unit = 'CNES Julian day'
        vt[:] = time
        
        # variables 2D
        for v in d2d:
            ncv = nc.createVariable(v, 'f8', dimensions=('x','y'))
            ncv.units = d2d[v]['units']
            ncv.description = d2d[v]['description']
            ncv[:] = d2d[v]['data']
        
        # variables 4d 
        for v in d4d:
            ncv = nc.createVariable(v, 'f8', dimensions=('x','y','t','t'))
            ncv.units = d4d[v]['units']
            ncv.description = d4d[v]['description']
            ncv[:] = d4d[v]['data']
        