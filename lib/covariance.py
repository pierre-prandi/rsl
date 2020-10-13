#!/usr/bin/env python
# coding: utf-8

"""
    covariance matrices
    implements three models for covariances: 
    - correlated noise
    - drift
    - bias
"""

import numpy as np

class Covariance():
    
    def __init__(self, x):
        self._size = len(x)
        self._x = x
        self._timestep = x[1] - x[0]
        self._matrix = np.zeros((self._size, self._size))
        
    def add_noise(self, variance, length):
        ''' 
            add a noise covariance
            variance:       level of variance of the noise
            lenfth:         decorellation scale 
        '''
        period = float(length/self._timestep)
        timeM = np.zeros((self._size, self._size))
        for i in np.arange(self._size):
            timeM[i,:] = np.arange(self._size)
        distanceM = np.subtract(timeM, np.transpose(timeM))
        matrix = variance*np.exp(-0.5*(distanceM/period)**2)
        self._matrix += matrix
        
    def add_drift(self, drift):
        ''' 
            add a drfit covariance
            drift:       1 sigma level of the drift
        '''
        timeM = np.zeros((self._size, self._size))
        for i in np.arange(self._size):
            timeM[i,:] = np.sqrt(2.0)*drift*self._x
        distanceM = abs(timeM - np.transpose(timeM))
        distanceM = distanceM - np.mean(distanceM, axis=0)
        matrix = np.dot(np.transpose(distanceM),distanceM)/(self._size-1.0)
        self._matrix += matrix
        
    def add_bias(self, bias, timing):
        '''
            add a bias covariance
            bias:       1 sigma level of teh bias
            timing:     date of the bias
        '''
        matrix = np.zeros((self._size, self._size))
        index = self.__time2Index(timing)
        factor = float(index)/self._size
        matrix[0:index, 0:index] = bias*(1.0 - factor)
        matrix[index:self._size, index:self._size] = bias*factor
        matrix = matrix - np.mean(matrix)
        self._matrix += matrix
    
    def __time2Index(self, date):
        '''
        conversion date -> index
        '''
        if date < self._x[0] or date > self._x[-1]:
            raise Exception("date %s is out of bounds" %(date))
        else:
            return np.where(self._x >= date)[0][0]
    
    @property
    def omega(self):
        return self._matrix
