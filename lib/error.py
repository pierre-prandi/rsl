#!/usr/bin/env python
# coding: utf-8

'''
    error manipulation class
'''
import logging
import numpy as np
import pyinterp
from netCDF4 import Dataset


class Error(object):
    
    def __init__(self, d):
        ''' constructor '''
        # check error type
        self._type = d['type']
        if self._type not in ['bias', 'noise', 'drift']:
            raise Exception("error type should be noise, bias or drift, type %s unexpected" %self._type)
        
        # check that required keys are defined
        self.__check_keys(d)
        
        # error levels
        if 'source' in d.keys():
            # error levels are read from a netCDF grid file
            if 'variable' not in d.keys():
                raise Exception("variable kwd should be defined")
            if 'factor' not in d.keys():
                raise Exception("factor kwd should be defined")
            self._unique_value = False
            self._load_file(d['source'], d['variable'], d['factor'])
            self._build_interpolator()

        elif 'value' in d.keys():
            # unique error level (=single value)
            self._unique_value = True
            self._value = d['value']

        else:
            # all other cases
            raise Exception("errors should be initiated with a value or a source file")
            
        # extra parameters for noises and biases
        if self._type == 'bias':
            self._timing = d['timing']
        elif self._type == 'noise':
            self._timescale = d['timescale']
    
    def __check_keys(self, d):
        ''' check that we got all the info needed to define the error '''
        
        # there should be either a source or value keyward in all cases
        if 'source' not in d.keys() and 'value' not in d.keys():
            raise Exception("either source or value kwd should be defined")
        
        # depending on the error type required kwd differ
        if self._type == 'bias':
            required = ['timing']
        elif self._type == 'noise':
            required = ['timescale']
        else:
            required = []
        
        # check
        for kwd in required:
            if kwd not in d.keys():
                raise Exception("kwd %s should be defined for a %s error" %(kwd, self._type))
        
    def _load_file(self, filename, varname, factor, lon='longitude', lat='latitude'):
        ''' load netcdf file '''
        logging.debug('loading from file %s' %filename)
        self._filename = filename
        # load the data
        with Dataset(filename, 'r') as nc:
            self._x = nc.variables[lon][:]
            self._y = nc.variables[lat][:]
            self._z = nc.variables[varname][:]
        
        if not np.ma.is_masked(self._z):
            self._z = np.ma.array(self._z, mask = np.full(np.shape(self._z), False, dtype=bool))
        
        self._z = self._z * factor**2
        
    def value(self, x, y):
        ''' return the error value at a given point '''
        if self._unique_value:
            return self._value
        else:
            return self._get_value_at_position(x, y)
            
    def _get_value_at_position(self, x, y):
        """
            interpolate grid value at given x/y position
        """
        ev = pyinterp.bivariate(self._grid, np.array([x]), np.array([y]))
        return ev.item()
        
    def _build_interpolator(self):
        """
            build interpolation function
        """
        x_axis = pyinterp.Axis(self._x, is_circle=True)
        y_axis = pyinterp.Axis(self._y)
        self._z[self._z.mask] = float("nan")
        self._grid = pyinterp.Grid2D(x_axis, y_axis, self._z.data)
        

    @property
    def type(self):
        return self._type
    
    @property
    def timing(self):
        return self._timing
        
    @property
    def timescale(self):
        return self._timescale            
    
    @property
    def data(self):
        return self._z


