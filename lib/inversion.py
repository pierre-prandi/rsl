#!/usr/bin/env python
# coding: utf-8

"""
    inversion methods
"""

import numpy as np

def inversion_ols_any_degree(x, y, omega, deg=1):
    '''
    input:
        x: array of size n
        y: array of size n
        omega: array size n*n (error covariance matrix)
        deg: degree of the fit (deg=1 will fit y=a0+a1*x)
    returns:
        bh: array of fitted coefficients
        vbh: array of std error of fitted coefficients
    '''

    nx = len(x)
    X = np.empty((nx,deg+1))
    
    # normalisation
    x_mean = np.mean(x)
    x_range = np.max(x) - np.min(x)
    x_adim = (x-x_mean)/x_range
    for i in np.arange(deg+1):
        X[:,i] = x_adim**i
    
    # inversion
    XtX_inv = np.linalg.inv(np.dot(np.transpose(X), X))
    bh = np.dot(XtX_inv, np.dot(np.transpose(X), y))
    vbh = np.sqrt(np.diag(np.dot(np.dot(np.dot(np.dot(XtX_inv, X.T), omega), X), XtX_inv)))
    
    # expression dans l'espace dimensionnel
    for i in range(deg+1):
        bh[i] *= x_range**(-i)
        vbh[i] *= x_range**(-i)
  
    return bh, vbh
    


