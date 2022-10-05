#!/usr/bin/env python
# coding: utf-8

'''
    I/O utilities
'''

from netCDF4 import Dataset
from timeserie import Timeserie
import numpy as np

def loader(fname,
    varname,
    load_type='grid',
    lon='longitude',
    lat='latitude',
    time='time'):
    """
    wrapper for different data loaders
    """
    if load_type=='grid':
        return grid_loader(fname, varname, lon=lon, lat=lat, time=time)
    elif load_type=='cci':
        return cci_loader(fname, varname, lon=lon, lat=lat, time=time)
    else:
        raise Exception(f"load_type {load_type} unknown")

def cci_loader(fname, varname, lon='longitude', lat='latitude', time='time'):
    """
    reads data from CCI virtual coastal stations files
    """
    outdict = {}
    with Dataset(fname, 'r') as nc:
        longitudes = nc.variables[lon][:]
        latitudes = nc.variables[lat][:]
        dates = np.variables[time][:]
        sla = nc.variables[varname][:]
    (npoints, ntimes) = np.shape(sla)
    for ipt in np.arange(npoints):
        key = (longitudes[ipt], latitude[ipt])
        value = Timeserie(dates, sla[ipt,:].filled(np.nan))
        outdict[key] = value
    return outdict

def grid_loader(fname, 
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
        