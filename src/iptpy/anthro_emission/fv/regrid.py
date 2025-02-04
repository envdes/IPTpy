import os
import numpy as np
import pandas as pd
import xarray as xr
import esmpy as ESMF
import xesmf as xe
import datetime


class Regrid(object):
    """
    Regrid class for regridding CAMS or CEDS anthropogenic emissions (monthly) to the CESM global fv grid. 
    CAMS-GLOB-ANTv5.3 (monthly) data is downloaded from: https://eccad.sedoo.fr by year.
    CEDS data is downloaded through the PNNL DataHub portal in GLOBUS, endpoint UUID: f58973c0-08c1-43a7-9a0e-71f54ddc973. See more details in: https://data.pnnl.gov/dataset/CEDS-4-21-21.

    Parameters
    ----------
    input_path : str
        Path to input CAMS or CEDS sum-up data.

    output_path : str
        Path to output regridded files.

    start_year : int
        Starting year for processing.

    end_year : inr
        Ending year for processing.

    source : str.
        Data source.

    version : str, optional                                   
        Data version, either 'v5.3' for CAMS or 'v2021-04-21' for CEDS.

    original_resolution : str, optional
        Original resolution of the input data, either '0.1x0.1' for CAMS or '0.5x0.5' for CEDS.

    regridder_filename : str, optional
        Filename to save the regridder object.

    original_lat : list, optional
        Original latitude grid.

    origional_lon : list, optional
        Original longitude grid.

    cdate : str, optional
        Creation date for output files, default is current date.
    
    timestep : str, optional
        Data timestep, default is 'monthly'.

    target_resolution : str, optional
        Target resolution for output, default is '0.9x1.25'.

    target_lat : list, optional          
        Target latitude grid. Uses default values if not specified.

    target_lon : list, optional        
        Target longitude grid. Uses default values if not specified.

    var_name : str, optional    
        Variable name in output files, default is 'emiss_anthro'. 

    sourcedata_var_list: : list, optional     
        List of CAMS or CEDS variables to process, default is all variables.

    model_var_list : list, optional    
        List of corresponding model variables. Automatically mapped if not provided.
    """
    def __init__(self,
                 input_path: str,
                 output_path: str,
                 start_year: int,
                 end_year: int,
                 source: str,
                 start_month: int = None,
                 end_month: int = None,
                 version: str = None,
                 original_resolution: str = None,
                 regridder_filename: str = None,
                 original_lat: list = None,
                 original_lon: list = None,
                 cdate: str = None,
                 timestep: str = 'monthly',
                 target_resolution: str = '0.9x1.25',
                 target_lat: list = None,
                 target_lon: list = None,
                 var_name: str = 'emiss_anthro',
                 sourcedata_var_list: list = None,
                 model_var_list: list = None):
        """
        This is the __init__ method docstring for Regrid.
        """
        self._source = source
        if source not in ['CAMS-GLOB-ANT', 'CEDS']:
            raise ValueError('source must be either CAMS-GLOB-ANT or CEDS')   
        self._target_resolution = target_resolution
        if target_resolution not in ['0.9x1.25']:
            raise ValueError('target_resolution must be 0.9x1.25')
        self._start_year = start_year
        self._end_year = end_year
        if start_year > end_year:
            raise ValueError('start_year must be less than or equal to end_year')
        self._input_path = input_path
        self._output_path = output_path
        if os.path.exists(output_path) == False:
            os.makedirs(output_path)
            print(f'Created directory {output_path}')
        if os.path.exists(input_path) == False:
            raise ValueError('input_path does not exist')  
        self._timestep = timestep
        if cdate is None:
            self._cdate = datetime.datetime.now().strftime('%Y%m%d')
        else:
            self._cdate = cdate
        
        if version is None:
            if source == 'CAMS-GLOB-ANT':
                version = 'v5.3'
            else:
                version = 'v2021-04-21'
        self._version = version    
        if original_resolution is None:
            if source == 'CAMS-GLOB-ANT':
                original_resolution = '0.1x0.1'
            else:
                original_resolution = '0.5x0.5'
        if source == 'CAMS-GLOB-ANT':
            first_year = 2000
            last_year = datetime.datetime.now().year - 1
            if version not in ['v5.3']:
               raise ValueError('version must be v5.3 for CAMS-GLOB-ANT') 
            if original_resolution not in ['0.1x0.1']:
               raise ValueError('original_resolution must be 0.1x0.1 for CAMS-GLOB-ANT')
        elif source == 'CEDS':
            first_year = 1750
            last_year = 2020
            if version not in ['v2021-04-21']:
               raise ValueError('version must be v2021-04-21 for CEDS')
            if original_resolution not in ['0.5x0.5']:
               raise ValueError('original_resolution must be 0.5x0.5 for CEDS')
        if start_year < first_year:
            raise ValueError('start_year must be greater than or equal to ' + str(first_year))
        if end_year > last_year:
            raise ValueError('end_year must be less than or equal to ' + str(last_year))
        if start_month is None:
            self._start_month = 1
        else:
            self._start_month = start_month    
        if end_month is None:
            self._end_month = 12    
        else:
            self._end_month = end_month    
        if self._end_year + self._end_month/12 <= self._start_year + self._start_month/12:
            raise ValueError('end_year and end_month must be greater than start_year and start_month')  
        self._original_resolution = original_resolution     
        grid_spacing = float(self._original_resolution.split('x')[0])
        self._original_lat = np.arange(-90, 90, grid_spacing).tolist()
        self._original_lon = np.arange(0, 360, grid_spacing).tolist()
        if target_lat is None:
            self._target_lat = [-90.      , -89.057594, -88.11518 , -87.172775, -86.23037 , -85.28796 ,
                      -84.34555 , -83.403145, -82.46073 , -81.518326, -80.57591 , -79.63351 ,
                      -78.6911  , -77.74869 , -76.80628 , -75.86388 , -74.92146 , -73.97906 ,
                      -73.03665 , -72.09424 , -71.15183 , -70.20943 , -69.26701 , -68.32461 ,
                      -67.3822  , -66.43979 , -65.49738 , -64.55498 , -63.612564, -62.67016 ,
                      -61.72775 , -60.78534 , -59.842934, -58.900524, -57.958115, -57.015705,
                      -56.0733  , -55.13089 , -54.18848 , -53.246075, -52.303665, -51.361256,
                      -50.41885 , -49.47644 , -48.53403 , -47.59162 , -46.649216, -45.706806,
                      -44.764397, -43.82199 , -42.87958 , -41.937172, -40.994766, -40.052357,
                      -39.109947, -38.167538, -37.225132, -36.282722, -35.340313, -34.397907,
                      -33.455498, -32.51309 , -31.57068 , -30.628273, -29.685863, -28.743456,
                      -27.801046, -26.858639, -25.916231, -24.973822, -24.031414, -23.089005,
                      -22.146597, -21.20419 , -20.26178 , -19.319372, -18.376963, -17.434555,
                      -16.492147, -15.549738, -14.607329, -13.664922, -12.722513, -11.780105,
                      -10.837696,  -9.895288,  -8.95288 ,  -8.010471,  -7.068063,  -6.125654,
                      -5.183246,  -4.240838,  -3.298429,  -2.356021,  -1.413613,  -0.471204,
                      0.471204,   1.413613,   2.356021,   3.298429,   4.240838,   5.183246,
                      6.125654,   7.068063,   8.010471,   8.95288 ,   9.895288,  10.837696,
                      11.780105,  12.722513,  13.664922,  14.607329,  15.549738,  16.492147,
                      17.434555,  18.376963,  19.319372,  20.26178 ,  21.20419 ,  22.146597,
                      23.089005,  24.031414,  24.973822,  25.916231,  26.858639,  27.801046,
                      28.743456,  29.685863,  30.628273,  31.57068 ,  32.51309 ,  33.455498,
                      34.397907,  35.340313,  36.282722,  37.225132,  38.167538,  39.109947,
                      40.052357,  40.994766,  41.937172,  42.87958 ,  43.82199 ,  44.764397,
                      45.706806,  46.649216,  47.59162 ,  48.53403 ,  49.47644 ,  50.41885 ,
                      51.361256,  52.303665,  53.246075,  54.18848 ,  55.13089 ,  56.0733  ,
                      57.015705,  57.958115,  58.900524,  59.842934,  60.78534 ,  61.72775 ,
                      62.67016 ,  63.612564,  64.55498 ,  65.49738 ,  66.43979 ,  67.3822  ,
                      68.32461 ,  69.26701 ,  70.20943 ,  71.15183 ,  72.09424 ,  73.03665 ,
                      73.97906 ,  74.92146 ,  75.86388 ,  76.80628 ,  77.74869 ,  78.6911  ,
                      79.63351 ,  80.57591 ,  81.518326,  82.46073 ,  83.403145,  84.34555 ,
                      85.28796 ,  86.23037 ,  87.172775,  88.11518 ,  89.057594,  90.      ]
        else:
            self._target_lat = target_lat
        if target_lon is None:
            self._target_lon = np.arange(0, 360, 1.25)
        else:        
            self._target_lon = target_lon
        self._var_name = var_name
        self._regridder_filename = regridder_filename
        if os.path.exists(self._regridder_filename) == False:
            print('regridder_filename does not exist. Please create a regridder first using the generate_regridder method.')
        # Initialize the variable lists
        full_sourcedata_var_list = []  # Default value in case no source matches
        model_mapping = {}

        if source == 'CAMS-GLOB-ANT':
            full_sourcedata_var_list = ['bc', 'co', 'nh3', 'nox', 'oc', 'so2', 
                                        'alcohols', 'ethane', 'propane', 'butanes', 
                                        'pentanes', 'hexanes', 'ethene', 'propene',
                                        'acetylene', 'other-alkenes-and-alkynes', 'benzene', 'toluene',
                                        'xylene', 'trimethylbenzene', 'other-aromatics', 'esters', 
                                        'ethers', 'formaldehyde', 'other-aldehydes', 'total-ketones',
                                        'total-acids']
            model_mapping = {'bc': 'bc', 'co': 'co', 'nh3': 'nh3', 'nox': 'nox', 'oc': 'oc', 'so2': 'so2',
                             'alcohols': 'alcohols', 'ethane': 'ethane', 'propane': 'propane','butanes': 'butanes', 
                             'pentanes': 'pentanes', 'hexanes': 'hexanes', 'ethene': 'ethene', 'propene': 'propene', 
                             'acetylene': 'ethyne', 'other-alkenes-and-alkynes': 'other-alkenes-and-alkynes', 'benzene': 'benzene', 'toluene': 'toluene',
                             'xylene': 'xylene', 'trimethylbenzene': 'trimethylbenzene', 'other-aromatics': 'other-aromatics', 'esters': 'esters', 
                             'ethers': 'ethers', 'formaldehyde': 'methanal', 'other-aldehydes': 'other-aldehydes', 'total-ketones': 'ketones', 
                             'total-acids': 'acids'}
        elif source == 'CEDS':
            full_sourcedata_var_list = ['BC', 'CO', 'NH3', 'NOx', 'OC', 'SO2',
                                        'VOC01-alcohols', 'VOC02-ethane', 'VOC03-propane', 'VOC04-butanes', 
                                        'VOC05-pentanes', 'VOC06-hexanes', 'VOC07-ethene', 'VOC08-propene',
                                        'VOC09-ethyne', 'VOC12-other', 'VOC13-benzene', 'VOC14-toluene',
                                        'VOC15-xylene', 'VOC16-trimethylb', 'VOC17-other', 'VOC18-esters',
                                        'VOC19-ethers', 'VOC21-methanal', 'VOC22-other', 'VOC23-ketones',
                                        'VOC24-acids']
            model_mapping = {'BC': 'bc', 'CO': 'co', 'NH3': 'nh3', 'NOx': 'nox', 'OC': 'oc', 'SO2': 'so2',
                             'VOC01-alcohols': 'alcohols', 'VOC02-ethane': 'ethane', 'VOC03-propane': 'propane',
                             'VOC04-butanes': 'butanes', 'VOC05-pentanes': 'pentanes', 'VOC06-hexanes': 'hexanes',
                             'VOC07-ethene': 'ethene', 'VOC08-propene': 'propene', 'VOC09-ethyne': 'ethyne',
                             'VOC12-other': 'other-alkenes-and-alkynes', 'VOC13-benzene': 'benzene', 'VOC14-toluene': 'toluene',
                             'VOC15-xylene': 'xylene', 'VOC16-trimethylb': 'trimethylbenzene', 'VOC17-other': 'other-aromatics',
                             'VOC18-esters': 'esters', 'VOC19-ethers': 'ethers', 'VOC21-methanal': 'methanal',
                             'VOC22-other': 'other-aldehydes', 'VOC23-ketones': 'ketones', 'VOC24-acids': 'acids'}

        if sourcedata_var_list is None:
            sourcedata_var_list = full_sourcedata_var_list    
        invalid_vars = [var for var in sourcedata_var_list if var not in full_sourcedata_var_list]
        if invalid_vars:
            raise ValueError(f"Invalid variables in var_list: {invalid_vars}. "
                             f"Valid options are: {full_sourcedata_var_list}.")  
        self._sourcedata_var_list = sourcedata_var_list    
        self._model_var_list = [model_mapping[var] for var in sourcedata_var_list if var in model_mapping]
    
    def generate_regridder(self):
        """
        Generate regridder object for regridding CAMS or CEDS anthropogenic emissions to the CESM grid.
        """
        original_grid = xr.Dataset({'lat': self._original_lat, 'lon': self._original_lon})
        target_grid = xr.Dataset({'lat': self._target_lat, 'lon': self._target_lon})
        regridder = xe.Regridder(original_grid, target_grid, 'conservative', periodic=True)  
        if self._regridder_filename is None:
            print('Please provide a regridder_filename to save the regridder object.')
        if os.path.exists(self._regridder_filename):
            os.remove(self._regridder_filename)
            print(f'Removed existing regridder file {self._regridder_filename} and created a new one.')    
        regridder.to_netcdf(self._regridder_filename)
    
    def apply_regridder(self):
        """
        Apply regridder object to regrid CAMS or CEDS anthropogenic emissions to the CESM grid.
        """
        original_grid = xr.Dataset({'lat': self._original_lat, 'lon': self._original_lon})
        target_grid = xr.Dataset({'lat': self._target_lat, 'lon': self._target_lon})
        regridder = xe.Regridder(original_grid, target_grid, 'conservative', periodic=True, reuse_weights=True, weights=self._regridder_filename)
        for source_var, model_var in zip(self._sourcedata_var_list, self._model_var_list):
            print(f'Regridding {source_var} ...')
            if self._source == 'CAMS-GLOB-ANT':  
                date = '01'  
                dataset = []
                for year in range(self._start_year, self._end_year + 1):
                    # the CAMS data is downloaded and stored by year
                    ds = xr.open_dataset(f'{self._input_path}{year}/{self._source}_Glb_{self._original_resolution}_anthro_{source_var}_{self._version}_{self._timestep}_{year}.nc')
                    source_ds = ds['sum'].to_dataset(name=self._var_name)
                    rolled_source_ds = source_ds.roll(lon=1800, roll_coords=True)
                    rolled_source_ds['lon'] = xr.where(rolled_source_ds['lon'] < 0, 
                                                   rolled_source_ds['lon'] + 360, 
                                                   rolled_source_ds['lon'])
                    rolled_source_ds = rolled_source_ds.assign_coords(lon = self._original_lon, lat = self._original_lat)
                    regridded_ds = regridder(rolled_source_ds)
                    dataset.append(regridded_ds)
                output_ds = xr.concat(dataset, dim='time')
                sel_output_ds = output_ds.sel(time=slice(f'{self._start_year}-{self._start_month}-01', f'{self._end_year}-{self._end_month}-01'))
                output_filename = f'{self._output_path}{self._source}_{self._original_resolution}_anthro_{model_var}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc'
                if os.path.exists(output_filename):
                   os.remove(output_filename)
                sel_output_ds.to_netcdf(output_filename)
                if source_var == 'so2':
                    print('Regridding each sector for SO2 ...')
                    sector_list = ['awb', 'ene', 'fef', 'ind', 'ref', 'res', 'shp', 'swd', 'tnr', 'tro']
                    for sector in sector_list:
                        dataset = []
                        for year in range(self._start_year, self._end_year + 1):
                            ds = xr.open_dataset(f'{self._input_path}{year}/{self._source}_Glb_{self._original_resolution}_anthro_{source_var}_{self._version}_{self._timestep}_{year}.nc') 
                            source_ds = ds[sector].to_dataset(name=self._var_name)
                            rolled_source_ds = source_ds.roll(lon=1800, roll_coords=True)
                            rolled_source_ds['lon'] = xr.where(rolled_source_ds['lon'] < 0, 
                                           rolled_source_ds['lon'] + 360, 
                                           rolled_source_ds['lon'])
                            rolled_source_ds = rolled_source_ds.assign_coords(lon = self._original_lon, lat = self._original_lat)
                            regridded_ds = regridder(rolled_source_ds)
                            dataset.append(regridded_ds)
                        output_ds = xr.concat(dataset, dim='time')
                        output_filename = f'{self._output_path}{self._source}_{self._original_resolution}_anthro_{model_var}_{sector}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc'
                        if os.path.exists(output_filename):
                           os.remove(output_filename)
                        output_ds.to_netcdf(output_filename)
            elif self._source == 'CEDS':
                date = '16'
                ds = xr.open_dataset(f'{self._input_path}{model_var}_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_0.5_c{self._cdate}.nc')
                rolled_source_ds = ds.roll(lon=360, roll_coords=True)
                rolled_source_ds['lon'] = xr.where(rolled_source_ds['lon'] < 0, 
                                                   rolled_source_ds['lon'] + 360, 
                                                   rolled_source_ds['lon'])
                rolled_source_ds = rolled_source_ds.assign_coords(lon = self._original_lon, lat = self._original_lat)
                regridded_ds = regridder(rolled_source_ds)
                output_filename = f'{self._output_path}{self._source}_{self._original_resolution}_anthro_{model_var}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc'
                if os.path.exists(output_filename):
                    os.remove(output_filename)
                regridded_ds.to_netcdf(output_filename)
                if source_var == 'SO2':
                    print('Regridding each sector for SO2 ...')
                    sector_list = ['agr', 'ene', 'ind', 'tra', 'res', 'sol', 'was', 'shp']
                    for sector in sector_list:
                        ds = xr.open_dataset(f'{self._input_path}{model_var}_{sector}_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_0.5_c{self._cdate}.nc')
                        rolled_source_ds = ds.roll(lon=360, roll_coords=True)
                        rolled_source_ds['lon'] = xr.where(rolled_source_ds['lon'] < 0, 
                                                       rolled_source_ds['lon'] + 360, 
                                                       rolled_source_ds['lon'])
                        rolled_source_ds = rolled_source_ds.assign_coords(lon = self._original_lon, lat = self._original_lat)
                        regridded_ds = regridder(rolled_source_ds)
                        output_filename = f'{self._output_path}{self._source}_{self._original_resolution}_anthro_{model_var}_{sector}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc'
                        if os.path.exists(output_filename):
                            os.remove(output_filename)
                        regridded_ds.to_netcdf(output_filename)
            
            

       
