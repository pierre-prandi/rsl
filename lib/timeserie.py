#!/usr/bin/env python
# coding: utf-8

'''
Holder for time series
'''

from dataclasses import dataclass

@dataclass
class Timeserie:
    time: np.ndarray
    ssha: np.ndarray
    