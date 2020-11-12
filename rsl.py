#!/usr/bin/env python
# coding: utf-8

'''
    perform the analysis of rmsl uncertainties
'''

import argparse
import os
import logging
import yaml

import numpy as np

from lib.io import loader, writer
from lib.error import Error
from lib.covariance import Covariance
from lib.inversion import els

# cli
parser = argparse.ArgumentParser()
parser.add_argument('yml', help='configuration file')
parser.add_argument('--debug', default=False, action='store_true', help='increase verbosity')
args = parser.parse_args()

# configure logging
level=logging.INFO
if args.debug:
    level = logging.DEBUG
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                    level=level)

# read conf file
logging.info('reading configuration from %s' %args.yml)
with open(args.yml, 'r') as f:
    conf = yaml.safe_load(f)

# load data 
logging.info('loading data from %s' %conf['input']['filename'])
x,y,t,z = loader(conf['input']['filename'],
    conf['input']['variable'])

# convert time/sla to desired units
tconv = t*conf['t_fact'] + conf['t_offset']
zconv = z*conf['z_fact']

# init errors
logging.info('init errors')
err_dict = {}
for err in conf['errors']:
    logging.debug('init error %s' %err)
    err_dict[err] = Error(conf[err])

# variables to store results
nx, ny, nt = len(x), len(y), len(t)
ng = nx*ny
trend, trendci = np.full((nx, ny), np.nan, dtype=float), np.full((nx, ny), np.nan, dtype=float)
accel, accelci = np.full((nx, ny), np.nan, dtype=float), np.full((nx, ny), np.nan, dtype=float)
covariances = np.full((nx,ny,nt,nt), np.nan, dtype=float)

# loop through grid points
logging.info('going through the grid...')
cnt = 1
for ilon, clon in enumerate(x):
    for ilat, clat in enumerate(y):
        logging.debug('processing cell %d/%d' %(cnt, ng))

        # extract the time series
        y_vals = zconv[ilon, ilat, :]

        # check for undefined values
        if np.any(np.isnan(y_vals)):
            logging.debug('incomplete time series')
            cnt+=1
            continue

        # create & populate the error covariance matrix
        covar = Covariance(tconv)
        for err in conf['errors']:
            c_err = err_dict[err]
            if c_err.type == 'bias':
                covar.add_bias(c_err.value(clon,clat), c_err.timing)
            if c_err.type == 'noise':
                covar.add_noise(c_err.value(clon,clat), c_err.timescale)
            if c_err.type == 'drift':
                covar.add_drift(c_err.value(clon,clat))
        covariances[ilon,ilat,:,:] = covar.omega

        # perform a linear fit & store results
        beta_hat, var_beta_hat = els(tconv, 
            y_vals, 
            covar.omega,
            deg=1)
        trend[ilon,ilat] = beta_hat[-1]
        trendci[ilon,ilat] = var_beta_hat[-1]*conf['ci_fact']

        # perform quadratic fit & store accelerations
        beta_hat, var_beta_hat = els(tconv, 
            y_vals, 
            covar.omega,
            deg=2)
        # acceleration = twice quadratic coeff
        accel[ilon,ilat] = beta_hat[-1]*2.
        accelci[ilon,ilat] = var_beta_hat[-1]*conf['ci_fact']
        cnt+=1

# were done, need to write output to a file
dvars_2d = {}
dvars_4d = {}

dvars_2d['trend']={
    'data' : np.ma.array(trend, mask=np.isnan(trend)),
    'units' : '%s/%s' %(conf['output_z_unit'], conf['output_t_unit']),
    'description' : 'sea level anomaly trend'
}
dvars_2d['trend_ci']={
    'data' : np.ma.array(trendci, mask=np.isnan(trendci)),
    'units' : '%s/%s' %(conf['output_z_unit'], conf['output_t_unit']),
    'description' : 'interval on sea level anomaly trend'
}
dvars_2d['accel']={
    'data' : np.ma.array(accel, mask=np.isnan(accel)),
    'units' : '%s/%s/%s' %(conf['output_z_unit'], conf['output_t_unit'], conf['output_t_unit']),
    'description' : 'sea level anomaly acceleration'
}
dvars_2d['accel_ci']={
    'data' : np.ma.array(accelci, mask=np.isnan(accelci)),
    'units' : '%s/%s/%s' %(conf['output_z_unit'], conf['output_t_unit'], conf['output_t_unit']),
    'description' : 'confidence interval on sea level anomaly acceleration'
}

dvars_4d['covariance']={
    'data': covariances,
    'units': '%s*%s' %(conf['output_z_unit'], conf['output_z_unit']),
    'description': 'error covariance matrix'
}

writer(conf['output'],
    x, y, t,
    dvars_2d,
    dvars_4d)