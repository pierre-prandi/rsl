# RLS

This repository holds the code necessary to reproduce the analysis presented in our paper on local sea level uncertainties which can be found [here](https://doi.org/10.1038/s41597-020-00786-7).

## requirements

This has been tested under Python 3.7.3 in an anaconda environment running in MacOS.
A list of all packages installed in this environment is available in the packages.txt file.

The NetCDF file containing the input data can be downloaded from [SEANOE](https://doi.org/10.17882/74862). This file is required to run the analysis.

## repository organisation

The script `rls.py` performs the analysis. It uses `rls.yml` as a configuration file. 
The main script relies on several libraries to deal with IO, error covariance models and inversion.
