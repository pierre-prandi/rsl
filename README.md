# RSL

This repository holds the code necessary to reproduce the analysis presented in our paper on local sea level uncertainties which can be found [here](https://doi.org/10.1038/s41597-020-00786-7).

The code loops through positions on the grid. 
At each position we 
1. construct the error covariance matrix from the errors defined in the configuration file,
2. build the linear system design matrix,
3. invert the system to get model parameters and their uncertainty.

Results are written to a netCDF file.

## requirements

This has been tested under Python 3.7.3 in an anaconda environment running in MacOS.
A list of all packages installed in this environment is available in the packages.txt file.

The NetCDF file containing the input data can be downloaded from [SEANOE](https://doi.org/10.17882/74862). This file is required to run the analysis.

## repository organisation

The script `rsl.py` performs the analysis. It uses `rls.yml` as a configuration file. 
The main script relies on several libraries to deal with IO, error covariance models and inversion.

## error prescription

The total error covariance matrix is estimated as the sum of all error terms, under an error independence hypothesis.
The errors are defined in the configuration file by dictionnaries:

```
tp_bias: {type: bias,
            value: 10.,
            timing: 1999.13}
```
the `type` key can take three values: `bias`, `noise` or `drift`.

Error amplitudes can be defined in the configuration file directly (in this case the same value is used at all prositions) or read from a gridded netCDF file (to allow for regional variations).
When reading from a netCDF file filepath, variable name and conversion factor (defaults to 1.) should be provided in the configuration.
### _biases_

`bias` errors are defined by an amplitude and a timing (when they occur).
Timing must be provided as a float (in converted time units) in the conf file.
Amplitude can either be provided as a float using the `value` key of read from a netCDF gridded file when providing `source` and `variable` keywords.

Both 
```
bias: {type: bias,
    value: 1.,
    timing: 2000.}
```
and
```
bias: {type: bias,
    source: /path/to/file.nc,
    variable: variable_name_in_nc_file,
    timing: 2000.}
```
are valid.

### _noises_

`noise` errors are defined by an amplitude and a correlation scale (`timescale`).
Correlations must be provided as a float (in converted time units) in the conf file.
Amplitude can either be provided as a float using the `value` key of read from a netCDF gridded file when providing `source` and `variable` keywords.

Both 
```
noise: {type: noise,
    value: 1.,
    timescale: 5.}
```
and
```
noise: {type: noise,
    source: /path/to/file.nc,
    variable: variable_name_in_nc_file,
    timescale: 5.}
```
are valid.

### _drifts_

`drift` errors are defined by an amplitude.
Amplitude can either be provided as a float using the `value` key of read from a netCDF gridded file when providing `source` and `variable` keywords.

Both 
```
drift_error_name: {type: drift,
    value: 1.}
```
and
```
drift_error_name: {type: drift,
    source: /path/to/file.nc,
    variable: variable_name_in_nc_file,
    factor: 1.}
```
are valid.









