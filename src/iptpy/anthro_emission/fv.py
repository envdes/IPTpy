import os
import numpy as np
import pandas as pd
import xarray as xr
import datetime
import netCDF4 as nc
import shutil as sh
import esmpy as ESMF
import xesmf as xe

class FV(object):
    """Anthropogenic emissions processing for the FV dycore in CESM.

    FV class for processing global anthropogenic emissions for the FV dycore in CESM.
    
    Parameters
    ----------
    preregrid_path : str
        Path to pre-regridded data.

    regridded_path : str
        Path to regridded data.
    
    regridder_filename : str
        Filename to save the regridder object. 

    source : str
        Data source. 

    version : str
        Anthropogenic emission data version, either is 'v5.3' or 'v6.2' for CAMS or 'v2021-04-21' for CEDS.
       
    start_year : int
        Starting year for processing.   

    end_year : int
        Ending year for processing.
    
    start_month : int, optional
        Starting month for processing, default is 1. 

    end_month : int, optional
        Ending month for processing, default is 12.
    
    download_method : str, optional 
        Method to download data, either 'wget' or 'globus', default is 'wget'.

    original_resolution : str, optional
        Original resolution of the data, either '0.1x0.1' for CAMS or '0.5x0.5' for CEDS.
    
    target_resolution : str, optional
        Target resolution for output, default is '0.9x1.25'.

    cdate : str, optional     
        Creation date for output files, default is current date.

    model_var_list : list, optional
        List of model variables, default is all variables. 

    Reference Links
    ----------
    - https: https://github.com/NCAR/IPT/tree/master/Emissions/CAMS_Anthropogenic  
    - https://ncar.github.io/CAM-chem/examples/functions/Regridding.html
    - https://wiki.ucar.edu/display/camchem/Emission+Inventories
    - https://wiki.ucar.edu/display/MUSICA/Regridding+emissions
    - https://wiki.ucar.edu/display/mozart4/Using+MOZART-4+output
    """

    def __init__(self,
                 preregrid_path: str,
                 regridded_path: str,
                 regridder_filename: str,
                 source: str,
                 version: str,
                 start_year: int,
                 end_year: int,
                 start_month: int = None,
                 end_month: int = None,
                 download_method: str = None,
                 original_resolution: str = None,
                 target_resolution: str = '0.9x1.25',
                 cdate: str = None,
                 model_var_list: list = None
                 ):
        """Initialize the FV class.
        """
        self._preregrid_path = preregrid_path
        self._regridded_path = regridded_path
        self._version = version
        for path in [self._preregrid_path, self._regridded_path]:
            if os.path.exists(path) == False:
                os.makedirs(path)
                print(f'Created directory: {path}')    
        self._source = source
        if source not in ['CAMS-GLOB-ANT', 'CEDS']:
            raise ValueError('source must be either CAMS-GLOB-ANT or CEDS')   
        self._timestep = 'monthly'
        self._target_resolution = target_resolution
        if target_resolution not in ['0.9x1.25']:
            raise ValueError('target_resolution must be 0.9x1.25')
        self._var_name = 'emiss_anthro'
        full_model_var_list = ['bc_a4', 'CO', 'NH3', 'NO', 'pom_a4', 'SO2', 
                               'C2H6', 'C3H8', 'C2H4', 'C3H6', 'C2H2', 'BIGENE', 
                               'BENZENE', 'TOLUENE', 'CH2O', 'CH3CHO', 'BIGALK', 'XYLENES', 
                               'CH3OH', 'C2H5OH', 'CH3COCH3', 'MEK', 'HCOOH',
                               'CH3COOH', 'IVOC']
        species_mapping = {'bc_a4': 'bc', 'CO': 'co', 'NH3': 'nh3', 'NO': 'nox', 'pom_a4': 'oc', 'SO2': 'so2', 
                             'C2H6': 'ethane', 'C3H8': 'propane', 'C2H4': 'ethene', 'C3H6': 'propene', 'C2H2': 'ethyne', 'BIGENE': 'other-alkenes-and-alkynes', 
                             'BENZENE': 'benzene', 'TOLUENE': 'toluene', 'CH2O': 'methanal', 'CH3CHO': 'other-aldehydes',
                             'BIGALK': ["butanes","pentanes","hexanes","esters","ethers"], 
                             'XYLENES': ['xylene', 'trimethylbenzene', 'other-aromatics'], 
                             'CH3OH': 'alcohols', 'C2H5OH': 'alcohols', 'CH3COCH3': 'ketones', 'MEK': 'ketones', 'HCOOH': 'acids',
                             'CH3COOH': 'acids', 'IVOC': ['C3H6', 'C3H8', 'C2H6', 'C2H4', 'BIGENE', 'BIGALK', 'CH3COCH3', 'MEK', 'CH3CHO', 'CH2O', 'BENZENE', 'TOLUENE', 'XYLENES']}  
        if model_var_list is None:
            self._model_var_list = full_model_var_list
        else:    
            self._model_var_list = model_var_list
        invalid_vars = [var for var in self._model_var_list if var not in full_model_var_list]
        if invalid_vars:
            raise ValueError(f"Invalid variables in model_var_list: {invalid_vars}. "
                             f"Valid options are: {full_model_var_list}.")  
        self._species_mapping = [species_mapping[var] for var in self._model_var_list] 
        if 'IVOC' in self._model_var_list:
            self._model_var_list.remove('IVOC')
            self._model_var_list.append('IVOC')
            required_sub_vars = {'C3H6', 'C3H8', 'C2H6', 'C2H4', 'BIGENE', 'BIGALK', 'CH3COCH3', 'MEK', 'CH3CHO', 'CH2O', 'BENZENE', 'TOLUENE', 'XYLENES'}
            missing_vars = required_sub_vars - set(self._model_var_list)  # Set difference for missing variables
            if missing_vars:
                print(f"IVOC is present in var_namelist but the following required sub-variables are missing: {missing_vars}. "
                      f"IVOC requires all of the following: {required_sub_vars}")
       
        sel_species_list = []
        for model_var in self._model_var_list:
            if not isinstance(species_mapping[model_var], list):
                sel_species_list.append(species_mapping[model_var])
            else:
                if model_var != 'IVOC':
                    sel_species_list.extend(species_mapping[model_var])
                else:
                    mapped_species = [species_mapping[var] for var in species_mapping['IVOC']]
                    flattened_species = [item for sublist in mapped_species for item in (sublist if isinstance(sublist, list) else [sublist])]
                    sel_species_list.extend(flattened_species)           
        self._species_list = np.unique(sel_species_list).tolist()

        if cdate is None:
            self._cdate = datetime.datetime.now().strftime('%Y%m%d')
        else:
            self._cdate = cdate

        if download_method is None:
            self._download_method = 'wget'
        else:
            self._download_method = download_method
        if source == 'CAMS-GLOB-ANT':
            def_version = ['v5.3', 'v6.2']
            def_original_resolution = '0.1x0.1'
            def_first_year = 2000
            def_last_year = datetime.datetime.now().year - 1
            sourcedata_var_mapping = {'bc': 'bc', 'co': 'co', 'nh3': 'nh3', 'nox': 'nox', 'oc': 'oc', 'so2': 'so2',
                                      'alcohols': 'alcohols', 'ethane': 'ethane', 'propane': 'propane','butanes': 'butanes', 'pentanes': 'pentanes', 'hexanes': 'hexanes', 'ethene': 'ethene', 'propene': 'propene', 
                                      'ethyne': 'acetylene', 'other-alkenes-and-alkynes': 'other-alkenes-and-alkynes', 'benzene': 'benzene', 'toluene': 'toluene','xylene': 'xylene', 
                                      'trimethylbenzene': 'trimethylbenzene', 'other-aromatics': 'other-aromatics', 'esters': 'esters', 'ethers': 'ethers', 'methanal': 'formaldehyde', 
                                      'other-aldehydes': 'other-aldehydes', 'ketones': 'total-ketones', 'acids': 'total-acids'}
        elif source == 'CEDS':
            def_version = ['v2021-04-21']
            def_original_resolution = '0.5x0.5'
            if self._download_method == 'wget':
                def_first_year = 1950
            else:     
                def_first_year = 1750
            def_last_year = 2019
            sourcedata_var_mapping = {'bc': 'BC', 'co': 'CO', 'nh3': 'NH3', 'nox': 'NOx', 'oc': 'OC', 'so2': 'SO2',
                                      'alcohols': 'VOC01-alcohols', 'ethane': 'VOC02-ethane', 'propane': 'VOC03-propane',
                                      'butanes': 'VOC04-butanes', 'pentanes': 'VOC05-pentanes', 'hexanes': 'VOC06-hexanes-pl',
                                      'ethene': 'VOC07-ethene', 'propene': 'VOC08-propene', 'ethyne': 'VOC09-ethyne',
                                      'other-alkenes-and-alkynes': 'VOC12-other-alke', 'benzene': 'VOC13-benzene', 'toluene': 'VOC14-toluene',
                                      'xylene': 'VOC15-xylene', 'trimethylbenzene': 'VOC16-trimethylb', 'other-aromatics': 'VOC17-other-arom',
                                      'esters': 'VOC18-esters', 'ethers': 'VOC19-ethers', 'methanal': 'VOC21-methanal',
                                      'other-aldehydes': 'VOC22-other-alka', 'ketones': 'VOC23-ketones', 'acids': 'VOC24-acids'}
        if self._version not in def_version:
            raise ValueError(f'version must be {def_version} for {source}')
        if original_resolution != def_original_resolution:
            raise ValueError(f'original_resolution must be {def_original_resolution} for {source}') 
        self._sourcedata_var_mapping = sourcedata_var_mapping    
        self._sourcedata_var_list = [self._sourcedata_var_mapping[var] for var in self._species_list]
        self._start_year = start_year
        self._end_year = end_year
        self._regridder_filename = regridder_filename
        if start_year > end_year:
            raise ValueError('start_year must be less than or equal to end_year')
        if start_year < def_first_year:
            raise ValueError(f'start_year must be greater than or equal to {def_first_year}')
        if end_year > def_last_year:
            raise ValueError(f'end_year must be less than or equal to {def_last_year}')  
        if original_resolution is None:
            self._original_resolution = def_original_resolution
        else:
            self._original_resolution = original_resolution

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
        self._target_lon = np.arange(0, 360, 1.25) 
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
        grid_spacing = float(self._original_resolution.split('x')[0])
        self._original_lat = np.arange(-90, 90, grid_spacing).tolist()
        self._original_lon = np.arange(0, 360, grid_spacing).tolist()

    def sum_up(self,
               input_path: str):
        """Aggregate CEDS across sectors.

        Sum up CEDS anthropogenic emissions (monthly) before regriding.
        
        The input_path is the path to the downloaded CEDS data. The summed up data is stored in the preregrid_path.

        Parameters
        ----------
        input_path : str
            Path to the downloaded CEDS data.
        """
        if self._source != 'CEDS':
            raise ValueError('source must be CEDS')
        if self._download_method != 'globus':
            raise ValueError('download_method must be globus')
        self._input_path = input_path
        if os.path.exists(input_path) == False:
            raise ValueError('input_path does not exist') 
        period_start_index = (self._start_year - 2000) * 12 + self._start_month - 1
        period_end_index = (self._end_year - 2000) * 12 + self._end_month - 1
        for source_var, species in zip(self._sourcedata_var_list, self._species_list):
            print(f'Summing up {source_var}')
            if source_var in ['BC', 'CO', 'NH3', 'NOx', 'OC', 'SO2']:
                filename = source_var + '-em-anthro'
                varname = source_var + '_em_anthro'
                data_path = self._input_path + source_var
                tag = '_gn_200001-201912.nc'
            else:
                filename = source_var + '-em-speciated-VOC-anthro'
                if source_var == 'VOC06-hexanes-pl':
                    data_path = self._input_path + 'VOC-speciated/VOC06-hexanes'
                elif source_var == 'VOC12-other-alke':   
                    data_path = self._input_path + 'VOC-speciated/VOC12-other'
                elif source_var == 'VOC17-other-arom':
                    data_path = self._input_path + 'VOC-speciated/VOC17-other'
                elif source_var == 'VOC22-other-alka':   
                    data_path = self._input_path + 'VOC-speciated/VOC22-other'  
                else:
                    data_path = self._input_path + 'VOC-speciated/' + source_var
                varname = source_var.replace("-", "_") + '_em_speciated_VOC_anthro'
                tag = '-supplemental-data_gn_200001-201912.nc'
            try:
                ds_path = f'{data_path}/individual_files/{filename}_input4MIPs_emissions_CMIP_CEDS-2021-04-21{tag}'
                ds_var = xr.open_dataset(ds_path)
            except FileNotFoundError:
                raise ValueError(f"File not found: {ds_path}")
                continue    
            ds_var_period = ds_var.sel(time=slice(ds_var.time[period_start_index], ds_var.time[period_end_index]))
        
            # special handling for SO2 emissions (individual sectors)
            if source_var == 'SO2':
                print('Saving individual sector files for SO2')
                sector_list = ['agr', 'ene', 'ind', 'tra', 'res', 'sol', 'was', 'shp']
                for i, sector in enumerate(sector_list):
                    output_filename = f'{self._preregrid_path}{species}_{sector}_anthro_{self._start_year}{int(self._start_month):02d}16_{self._end_year}{int(self._end_month):02d}16_0.5_c{self._cdate}.nc'
                    if os.path.exists(output_filename):
                        os.remove(output_filename)
                    renamed_da = ds_var_period[varname].sel(sector=i).rename(self._var_name)
                    renamed_da.attrs['long_name'] = ds_var_period[varname].attrs['long_name']
                    renamed_da.attrs['units'] = ds_var_period[varname].attrs['units']
                    renamed_da.attrs['cell_methods'] = ds_var_period[varname].attrs['cell_methods']
                    renamed_da.to_netcdf(output_filename) 
            else:  
                output_filename = f'{self._preregrid_path}{species}_anthro_{self._start_year}{int(self._start_month):02d}16_{self._end_year}{int(self._end_month):02d}16_0.5_c{self._cdate}.nc'
                if os.path.exists(output_filename):
                    os.remove(output_filename)      
                renamed_da = ds_var_period[varname].sum(dim='sector').rename(self._var_name)
                renamed_da.attrs['long_name'] = ds_var_period[varname].attrs['long_name']
                renamed_da.attrs['units'] = ds_var_period[varname].attrs['units']
                renamed_da.attrs['cell_methods'] = ds_var_period[varname].attrs['cell_methods']
                renamed_da.to_netcdf(output_filename)
                print(f'Saved {output_filename}')  
             

    def generate_regridder(self):
        """Generate a regridder using `xESMF <https://xesmf.readthedocs.io/en/stable/>`_.

        Generate regridder object for regridding CAMS or CEDS anthropogenic emissions to the CESM grid. The generated_regridder is stored in the regridder_filename.
        """
        original_grid = xr.Dataset({'lat': self._original_lat, 'lon': self._original_lon})
        target_grid = xr.Dataset({'lat': self._target_lat, 'lon': self._target_lon})
        regridder = xe.Regridder(original_grid, target_grid, 'conservative', periodic=True)  
        if os.path.exists(self._regridder_filename):
            os.remove(self._regridder_filename)
            print(f'Removed existing regridder file {self._regridder_filename} and created a new one.')    
        regridder.to_netcdf(self._regridder_filename)

    def apply_regridder(self):
        """Apply the regridder object.

        Apply regridder object to regrid CAMS or CEDS anthropogenic emissions to the CESM grid. The input data for regridding is stored in the preregrid_path and the regridded data is stored in the regridded_path. Regridder object is loaded from the regridder_filename and can be reused when running apply_regridder().
        """
        original_grid = xr.Dataset({'lat': self._original_lat, 'lon': self._original_lon})
        target_grid = xr.Dataset({'lat': self._target_lat, 'lon': self._target_lon})
        regridder = xe.Regridder(original_grid, target_grid, 'conservative', periodic=True, reuse_weights=True, weights=self._regridder_filename)
        for sourcedata_var, species in zip(self._sourcedata_var_list, self._species_list):
            print(f'Regridding {species} ...')
            if self._source == 'CAMS-GLOB-ANT':  
                nlon = 1800
                date = '01'
                if species == 'so2':
                    print('Regridding each sector for SO2 ...')
                    if self._version == 'v5.3':
                        sector_list = ['awb', 'ene', 'fef', 'ind', 'ref', 'res', 'shp', 'swd', 'tnr', 'tro']
                    else:
                        sector_list = ['awb', 'com', 'ene', 'fef', 'ind', 'ref', 'res', 'shp', 'tnr', 'tro']    
                    for sector in sector_list:
                        dataset = []
                        for year in range(self._start_year, self._end_year + 1):
                            ds = xr.open_dataset(f'{self._preregrid_path}{year}/{self._source}_Glb_{self._original_resolution}_anthro_{sourcedata_var}_{self._version}_{self._timestep}_{year}.nc') 
                            source_ds = ds[sector].to_dataset(name=self._var_name)
                            rolled_source_ds = source_ds.roll(lon=nlon, roll_coords=True)
                            rolled_source_ds['lon'] = xr.where(rolled_source_ds['lon'] < 0, 
                                           rolled_source_ds['lon'] + 360, 
                                           rolled_source_ds['lon'])
                            rolled_source_ds = rolled_source_ds.assign_coords(lon = self._original_lon, lat = self._original_lat)
                            regridded_ds = regridder(rolled_source_ds)
                            dataset.append(regridded_ds)
                        output_ds = xr.concat(dataset, dim='time')
                        output_filename = f'{self._regridded_path}{self._source}_{self._original_resolution}_anthro_{species}_{sector}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc'
                        if os.path.exists(output_filename):
                           os.remove(output_filename)
                        output_ds.to_netcdf(output_filename)
                else:
                    dataset = []
                    for year in range(self._start_year, self._end_year + 1):
                        # the CAMS data is downloaded and stored by year
                        ds = xr.open_dataset(f'{self._preregrid_path}{year}/{self._source}_Glb_{self._original_resolution}_anthro_{sourcedata_var}_{self._version}_{self._timestep}_{year}.nc')
                        source_ds = ds['sum'].to_dataset(name=self._var_name)
                        rolled_source_ds = source_ds.roll(lon=nlon, roll_coords=True)
                        rolled_source_ds['lon'] = xr.where(rolled_source_ds['lon'] < 0, 
                                                   rolled_source_ds['lon'] + 360, 
                                                   rolled_source_ds['lon'])
                        rolled_source_ds = rolled_source_ds.assign_coords(lon = self._original_lon, lat = self._original_lat)
                        regridded_ds = regridder(rolled_source_ds)
                        dataset.append(regridded_ds)
                    output_ds = xr.concat(dataset, dim='time')
                    sel_output_ds = output_ds.sel(time=slice(f'{self._start_year}-{self._start_month}-01', f'{self._end_year}-{self._end_month}-01'))
                    output_filename = f'{self._regridded_path}{self._source}_{self._original_resolution}_anthro_{species}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc'
                    if os.path.exists(output_filename):
                       os.remove(output_filename)
                    sel_output_ds.to_netcdf(output_filename)
            elif self._source == 'CEDS':
                nlon = 360
                date = '16'
                if self._download_method == 'globus':
                    if species == 'so2':
                        print('Regridding each sector for SO2 ...')
                        sector_list = ['agr', 'ene', 'ind', 'tra', 'res', 'sol', 'was', 'shp']
                        for sector in sector_list:
                            ds = xr.open_dataset(f'{self._preregrid_path}{species}_{sector}_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_0.5_c{self._cdate}.nc')
                            rolled_source_ds = ds.roll(lon=nlon, roll_coords=True)
                            rolled_source_ds['lon'] = xr.where(rolled_source_ds['lon'] < 0, 
                                                       rolled_source_ds['lon'] + 360, 
                                                       rolled_source_ds['lon'])
                            rolled_source_ds = rolled_source_ds.assign_coords(lon = self._original_lon, lat = self._original_lat)
                            regridded_ds = regridder(rolled_source_ds)
                            output_filename = f'{self._regridded_path}{self._source}_{self._original_resolution}_anthro_{species}_{sector}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc'
                            if os.path.exists(output_filename):
                                os.remove(output_filename)
                            regridded_ds.to_netcdf(output_filename)  
                    else:
                        ds = xr.open_dataset(f'{self._preregrid_path}{species}_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_0.5_c{self._cdate}.nc')
                        rolled_source_ds = ds.roll(lon=nlon, roll_coords=True)
                        rolled_source_ds['lon'] = xr.where(rolled_source_ds['lon'] < 0, 
                                                   rolled_source_ds['lon'] + 360, 
                                                   rolled_source_ds['lon'])
                        rolled_source_ds = rolled_source_ds.assign_coords(lon = self._original_lon, lat = self._original_lat)
                        regridded_ds = regridder(rolled_source_ds)
                        output_filename = f'{self._regridded_path}{self._source}_{self._original_resolution}_anthro_{species}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc'
                        if os.path.exists(output_filename):
                            os.remove(output_filename)
                        regridded_ds.to_netcdf(output_filename)
                elif self._download_method == 'wget':
                    if species == 'so2':
                        print('Regridding each sector for SO2 ...')
                        sector_mapping = {'agr':'agriculture', 'ene': 'energy', 'ind': 'industrial', 'res': 'residential', 'shp': 'ships', 'sol': 'solvents', 'tra': 'transportation', 'was': 'waste'}
                        for sector, sector_name in sector_mapping.items():
                            dataset = []
                            for year in range(self._start_year, self._end_year + 1):
                                ds = xr.open_dataset(f'{self._preregrid_path}{year}/CEDS_Glb_0.5x0.5_anthro_{sourcedata_var}__monthly_{year-1}.nc')
                                ds2 = xr.open_dataset(f'{self._preregrid_path}{year}/CEDS_Glb_0.5x0.5_anthro_{sourcedata_var}__monthly_{year}.nc')
                                ds_year_sector = xr.concat([ds[sector_name], ds2[sector_name]], dim='time')
                                source_ds = ds_year_sector.to_dataset(name=self._var_name)
                                rolled_source_ds = source_ds.roll(lon=nlon, roll_coords=True)
                                rolled_source_ds['lon'] = xr.where(rolled_source_ds['lon'] < 0, 
                                           rolled_source_ds['lon'] + 360, 
                                           rolled_source_ds['lon'])
                                rolled_source_ds = rolled_source_ds.assign_coords(lon = self._original_lon, lat = self._original_lat)
                                regridded_ds = regridder(rolled_source_ds)
                                dataset.append(regridded_ds)
                            output_ds = xr.concat(dataset, dim='time')
                            output_filename = f'{self._regridded_path}{self._source}_{self._original_resolution}_anthro_{species}_{sector}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc'
                            if os.path.exists(output_filename):
                               os.remove(output_filename)
                            output_ds.to_netcdf(output_filename)
                    else:
                        dataset = []
                        for year in range(self._start_year, self._end_year + 1):
                            ds = xr.open_dataset(f'{self._preregrid_path}{year}/CEDS_Glb_0.5x0.5_anthro_{sourcedata_var}__monthly_{year-1}.nc')
                            ds2 = xr.open_dataset(f'{self._preregrid_path}{year}/CEDS_Glb_0.5x0.5_anthro_{sourcedata_var}__monthly_{year}.nc')
                            ds_year_sector = xr.concat([ds['sum'], ds2['sum']], dim='time')  
                            source_ds = ds_year_sector.to_dataset(name=self._var_name)
                            rolled_source_ds = source_ds.roll(lon=nlon, roll_coords=True)
                            rolled_source_ds['lon'] = xr.where(rolled_source_ds['lon'] < 0, 
                                           rolled_source_ds['lon'] + 360, 
                                           rolled_source_ds['lon'])
                            rolled_source_ds = rolled_source_ds.assign_coords(lon = self._original_lon, lat = self._original_lat)
                            regridded_ds = regridder(rolled_source_ds)
                            dataset.append(regridded_ds)
                        output_ds = xr.concat(dataset, dim='time')
                        output_filename = f'{self._regridded_path}{self._source}_{self._original_resolution}_anthro_{species}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc'
                        if os.path.exists(output_filename):
                            os.remove(output_filename)
                        output_ds.to_netcdf(output_filename)  

    def rename(self,
               renamed_path: str,
               mw_mapping: dict = None, 
               sf_mapping: dict = None):
        """Rename the regridded data.
        
        Rename the emissions files to match the model inputs. The input data for renaming is stored in the regridded_path and the renamed data is stored in the renamed_path.

        Parameters
        ----------
        renamed_path : str
            Path to store the renamed files for simulation.
        
        mw_mapping : dict, optional    
            Molecular weight mapping for each species, default is the values used in the model. 
            User can provide a dictionary with the species as keys and the molecular weights as values.

        sf_mapping : dict, optional     
            Scale factor mapping for each species, default is the values used in the model.
            User can provide a dictionary with the species as keys and the scale factors as values.    
        """

        if mw_mapping is None:
            self._mw_mapping = {'bc_a4': 12, 'CO': 28, 'NH3': 17, 'NO': 30, 'pom_a4': 12, 'SO2': 64,
                      'C2H6': 30, 'C3H8': 44, 'C2H4': 28, 'C3H6': 42, 'C2H2': 26, 'BIGENE': 56, 
                      'BENZENE': 78, 'TOLUENE': 92, 'CH2O': 30, 'CH3CHO': 44, 'BIGALK': 72, 'XYLENES': 106, 
                      'CH3OH': 32, 'C2H5OH': 46, 'CH3COCH3': 58, 'MEK': 72, 'HCOOH': 46, 
                      'CH3COOH': 60, 'IVOC': 184, 
                      'butanes': 58, 'pentanes': 72, 'hexanes': 86, 'esters': 184, 'ethers': 81,
                      'xylene': 106, 'trimethylbenzene': 120, 'other-aromatics': 126,
                      }  
        else:
            self._mw_mapping = mw_mapping    
        if sf_mapping is None:
            self._sf_mapping = {'bc_a4': 1, 'CO': 1, 'NH3': 1, 'NO': 46/30, 'pom_a4': 1.4, 'SO2': 1,
                      'C2H6': 1, 'C3H8': 1, 'C2H4': 1, 'C3H6': 1, 'C2H2': 1, 'BIGENE': 1, 
                      'BENZENE': 1, 'TOLUENE': 1, 'CH2O': 1, 'CH3CHO': 1, 'BIGALK': 1, 'XYLENES': 1, 
                      'CH3OH': 0.15, 'C2H5OH': 0.85, 'CH3COCH3': 0.2, 'MEK': 0.8, 'HCOOH': 0.5, 
                      'CH3COOH': 0.5, 'IVOC': 0.2}
        else:
            self._sf_mapping = sf_mapping    
        
        mw_list = [self._mw_mapping[var] for var in self._model_var_list]
        sf_list = [self._sf_mapping[var] for var in self._model_var_list]

        time_units = "days since 2000-01-01 00:00:00"
        var_name = 'emiss_anthro'
        var_unit = 'molecules/cm2/s'
        num_var_unit = 'particles/cm2/s)(molecules/mole)(g/kg)'
        avogadro_number = 6.022e23 
        m2_to_cm2 = 1e4
        kg_to_g = 1e3
        unit_factor = avogadro_number * kg_to_g / m2_to_cm2
        periods = 12 * (self._end_year - self._start_year + 1)
        def mass_per_particle(rho, diam):
            return rho * (np.pi / 6.0) * (diam ** 3)
        if self._source == 'CAMS-GLOB-ANT':
            date = '01'
            print("Warning: CAMS emissions are monthly averages at the first of the month, for example, 2000-12-01.")
            new_time_values = pd.date_range(start=str(self._start_year) + '-01-01', periods=periods, freq='MS')    
        elif self._source == 'CEDS':
            date = '16'
            print("Warning: CEDS emissions are monthly averages at the middle of the month, for example, 2000-12-16.")
            new_time_values = pd.date_range(start=str(self._start_year) + '-01-01', periods=periods, freq='MS') + pd.DateOffset(days=15)
        new_time_numeric = nc.date2num(new_time_values.to_pydatetime(), units=time_units, calendar='noleap')
        date_values = new_time_values.strftime('%Y%m%d').astype(int)

        for species, model_var, mw, sf in zip(self._species_mapping, self._model_var_list, mw_list, sf_list):
            print(f'Renaming {model_var} ...')
            if model_var == 'SO2':
                rho = 1770
                mw2 = 115
                if self._source == 'CAMS-GLOB-ANT':
                    if self._version == 'v5.3':
                        ag_sol_was = ['awb', 'swd']
                    else:
                        ag_sol_was = ['awb', 'com']    
                    res_tra = ['res', 'tro', 'tnr']
                    ene_ind = ['ene', 'ind', 'ref', 'fef']
                elif self._source == 'CEDS':
                    ag_sol_was = ['agr', 'sol', 'was']
                    res_tra = ['res', 'tra']
                    ene_ind = ['ene', 'ind']
                shp = ['shp']
                SO2_anthro_ag_ship_res_filename = f"{renamed_path}{self._source}{self._version}_{model_var}_anthro-ag-ship-res_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                SO2_anthro_ene_filename = f"{renamed_path}{self._source}{self._version}_{model_var}_anthro-ene_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                so4_a1_anthro_ag_ship_filename = f"{renamed_path}{self._source}{self._version}_so4_a1_anthro-ag-ship_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                so4_a2_anthro_res_filename = f"{renamed_path}{self._source}{self._version}_so4_a2_anthro-res_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                so4_a1_anthro_ene_vertical_filename = f"{renamed_path}{self._source}{self._version}_so4_a1_anthro-ene-vertical_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                num_so4_a1_anthro_ag_ship_filename = f"{renamed_path}{self._source}{self._version}_num_so4_a1_anthro-ag-ship_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                num_so4_a2_anthro_res_filename = f"{renamed_path}{self._source}{self._version}_num_so4_a2_anthro-res_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                num_so4_a1_anthro_ene_vertical_filename = f"{renamed_path}{self._source}{self._version}_num_so4_a1_anthro-ene-vertical_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                for file in [SO2_anthro_ag_ship_res_filename, SO2_anthro_ene_filename, so4_a1_anthro_ag_ship_filename, 
                             so4_a2_anthro_res_filename, so4_a1_anthro_ene_vertical_filename]:
                    if os.path.exists(file):
                        os.remove(file)   
                    with nc.Dataset(file, 'w', format='NETCDF3_CLASSIC') as output:    
                        output.title = f'Anthropogenic emissions for {self._source}_({self._original_resolution}).'
                        time_dim = output.createDimension('time', None)  
                        lat_dim = output.createDimension('lat', 192)
                        lon_dim = output.createDimension('lon', 288)    
                        time_var = output.createVariable('time', 'f4', ('time',))
                        time_var.units = time_units
                        time_var.calendar = 'noleap'
                        lon_var = output.createVariable('lon', 'f4', ('lon',))
                        lon_var.units = 'degrees_east'
                        lon_var.long_name = 'Longitude'
                        lon_var[:] = self._target_lon
                        lat_var = output.createVariable('lat', 'f4', ('lat',))
                        lat_var.units = 'degrees_north'
                        lat_var.long_name = 'Latitude'
                        lat_var[:] = self._target_lat
                        date_var = output.createVariable('date', 'i4', ('time',))
                        date_var.format = 'YYYYMMDD'
                        date_var.long_name = 'Date'
                        output.variables['time'][:] = new_time_numeric
                        output.variables['date'][:] = date_values.astype(np.int32).values 
                        if file == SO2_anthro_ag_ship_res_filename:  
                            var_name1 = 'emiss_ag_sol_was'
                            new_var1 = output.createVariable(var_name1, 'f4', ('time', 'lat', 'lon'))
                            new_var1.units = var_unit  
                            var_name2 = 'emiss_res_tran'
                            new_var2 = output.createVariable(var_name2, 'f4', ('time', 'lat', 'lon'))
                            new_var2.units = var_unit 
                            var_name3 = 'emiss_ship'
                            new_var3 = output.createVariable(var_name3, 'f4', ('time', 'lat', 'lon'))
                            new_var3.units = var_unit
                            for so2_var, sector in zip([new_var1, new_var2, new_var3], [ag_sol_was, res_tra, shp]):
                                so2_var[:, :, :] = 0.0
                                for s in sector:
                                    ds_so2 = xr.open_dataset(f'{self._regridded_path}{self._source}_{self._original_resolution}_anthro_{species}_{s}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')
                                    so2_var[:, :, :] += ds_so2[var_name].values * 0.975 * ( unit_factor / mw )
  
                        if file == SO2_anthro_ene_filename:
                            var_name4 = 'emiss_ene_ind'
                            new_var4 = output.createVariable(var_name4, 'f4', ('time', 'lat', 'lon'))
                            new_var4.units = var_unit
                            new_var4[:, :, :] = 0.0
                            for s in ene_ind:
                                ds_so2 = xr.open_dataset(f'{self._regridded_path}{self._source}_{self._original_resolution}_anthro_{species}_{s}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')
                                new_var4[:, :, :] += ds_so2[var_name].values * 0.975 * ( unit_factor / mw )
        
                        if file == so4_a1_anthro_ag_ship_filename:
                            var_name1 = 'emiss_ag_sol_was'
                            new_var1 = output.createVariable(var_name1, 'f4', ('time', 'lat', 'lon'))
                            new_var1.units = var_unit  
                            var_name3 = 'emiss_ship'
                            new_var3 = output.createVariable(var_name3, 'f4', ('time', 'lat', 'lon'))
                            new_var3.units = var_unit
                            for so2_var, sector in zip([new_var1, new_var3], [ag_sol_was, shp]):
                                so2_var[:, :, :] = 0.0
                                for s in sector:
                                    ds_so2 = xr.open_dataset(f'{self._regridded_path}{self._source}_{self._original_resolution}_anthro_{species}_{s}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')
                                    so2_var[:, :, :] += ds_so2[var_name].values * 0.975 * ( unit_factor / mw )
                       
                        if file == so4_a2_anthro_res_filename:    
                            var_name4 = 'emiss_res_tran'
                            new_var4 = output.createVariable(var_name4, 'f4', ('time', 'lat', 'lon'))
                            new_var4.units = var_unit
                            new_var4[:, :, :] = 0.0
                            for s in res_tra:
                                ds_so2 = xr.open_dataset(f'{self._regridded_path}{self._source}_{self._original_resolution}_anthro_{species}_{s}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')
                                new_var4[:, :, :] += ds_so2[var_name].values * 0.975 * ( unit_factor / mw )
                
                        if file == so4_a1_anthro_ene_vertical_filename:  
                            vertical_levels = [0.025, 0.075, 0.125, 0.175, 0.225, 0.275, 0.325, 0.375]
                            vertical_levels_int = [0.  , 0.05, 0.1 , 0.15, 0.2 , 0.25, 0.3 , 0.35, 0.4 ]
                            altitude_dim = output.createDimension('altitude', len(vertical_levels))  
                            altitude_int_dim = output.createDimension('altitude_int', len(vertical_levels_int))
                            altitude_var = output.createVariable('altitude', 'f4', ('altitude',))
                            altitude_var.units = 'km'
                            altitude_var.long_name = 'Altitude'
                            altitude_int_var = output.createVariable('altitude_int', 'f4', ('altitude_int',))
                            altitude_int_var.units = 'km'
                            altitude_int_var.long_name = 'Altitude_int'
                            output.variables['altitude'][:] = vertical_levels
                            output.variables['altitude_int'][:] = vertical_levels_int 
                            var_name4 = 'emiss_ene_ind'
                            new_var4 = output.createVariable(var_name4, 'f4', ('time', 'altitude', 'lat', 'lon'))
                            new_var4.units = var_unit
                            new_var4[:, :, :, :] = 0.0
                            for s in ene_ind:
                                ds_so2 = xr.open_dataset(f'{self._regridded_path}{self._source}_{self._original_resolution}_anthro_{species}_{s}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')                    
                                layer_values = np.zeros_like(ds_so2[var_name].values)
                                layer_values += ds_so2[var_name].values * 0.025 * ( unit_factor / mw ) / 2e4
                            new_var4[:, 3:7, :, :] = layer_values[:, np.newaxis, :, :]
                
                if os.path.exists(num_so4_a1_anthro_ag_ship_filename):
                    os.remove(num_so4_a1_anthro_ag_ship_filename)
                sh.copy(so4_a1_anthro_ag_ship_filename, num_so4_a1_anthro_ag_ship_filename)
                with nc.Dataset(num_so4_a1_anthro_ag_ship_filename, 'r+') as input_ds:
                    input_ds['emiss_ag_sol_was'][:, :, :] *= mw2 /mass_per_particle(rho, 0.134e-6) #diam = 0.134e-6, 5.157170449543804e19
                    input_ds['emiss_ship'][:, :, :] *= mw2 /mass_per_particle(rho, 0.261e-6) #diam = 0.261e-6, 6.979181393389552e18   
                    input_ds['emiss_ag_sol_was'].units = num_var_unit
                    input_ds['emiss_ship'].units = num_var_unit
                
                if os.path.exists(num_so4_a2_anthro_res_filename):
                    os.remove(num_so4_a2_anthro_res_filename)   
                sh.copy(so4_a2_anthro_res_filename, num_so4_a2_anthro_res_filename)     
                with nc.Dataset(num_so4_a2_anthro_res_filename, 'r+') as input_ds:
                    input_ds['emiss_res_tran'][:, :, :] *= mw2 /mass_per_particle(rho, 0.0504e-6) #diam = 0.0504e-6, 9.692466974041687e20   
                    input_ds['emiss_res_tran'].units = num_var_unit
                
                if os.path.exists(num_so4_a1_anthro_ene_vertical_filename):
                    os.remove(num_so4_a1_anthro_ene_vertical_filename)
                sh.copy(so4_a1_anthro_ene_vertical_filename, num_so4_a1_anthro_ene_vertical_filename)    
                with nc.Dataset(num_so4_a1_anthro_ene_vertical_filename, 'r+') as input_ds:  
                    input_ds['emiss_ene_ind'][:, :, :, :] *= mw2 /mass_per_particle(rho, 0.261e-6) #diam = 0.261e-6, 6.979181393389552e18  
                    input_ds['emiss_ene_ind'].units = num_var_unit 
            else:        
                output_filename = f"{renamed_path}{self._source}{self._version}_{model_var}_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                if os.path.exists(output_filename):
                    os.remove(output_filename)
                with nc.Dataset(output_filename, 'w', format='NETCDF3_CLASSIC') as output:
                    output.title = f'Anthropogenic emissions for {self._source}_({self._original_resolution}).'
                    time_dim = output.createDimension('time', None)  # Unlimited dimension for time
                    lat_dim = output.createDimension('lat', 192)
                    lon_dim = output.createDimension('lon', 288)
                    time_var = output.createVariable('time', 'f4', ('time',))
                    time_var.units = time_units
                    time_var.calendar = 'noleap'
                    lon_var = output.createVariable('lon', 'f4', ('lon',))
                    lon_var.units = 'degrees_east'
                    lon_var.long_name = 'Longitude'
                    lon_var[:] = self._target_lon
                    lat_var = output.createVariable('lat', 'f4', ('lat',))
                    lat_var.units = 'degrees_north'
                    lat_var.long_name = 'Latitude'
                    lat_var[:] = self._target_lat
                    emis_var = output.createVariable(var_name, 'f4', ('time', 'lat', 'lon'))
                    emis_var.units = var_unit
                    date_var = output.createVariable('date', 'i4', ('time',))
                    date_var.format = 'YYYYMMDD'
                    date_var.long_name = 'Date'
        
                    output.variables['time'][:] = new_time_numeric
                    output.variables['date'][:] = date_values.astype(np.int32).values 
                    if isinstance(species, list):
                        output.variables[var_name][:, :, :] = 0
                    else:    
                        input_ds = xr.open_dataset(f'{self._regridded_path}{self._source}_{self._original_resolution}_anthro_{species}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')
                        output.variables[var_name][:, :, :] = input_ds[var_name][:, :, :].values * (unit_factor / mw) * sf
                
                if model_var == 'bc_a4':
                    rho = 1700
                    diam = 0.134e-6
                    num_output_filename = f"{renamed_path}{self._source}{self._version}_num_{model_var}_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                    if os.path.exists(num_output_filename):
                        os.remove(num_output_filename)
                    sh.copy(output_filename, num_output_filename)
                    with nc.Dataset(num_output_filename, 'r+') as num_ds:
                         num_ds.variables[var_name][:, :, :] *= mw /mass_per_particle(rho, diam) #5.60298303e18 
                         num_ds.variables[var_name].units = num_var_unit
            
                if model_var == 'CO':
                    hcn_mw = 27
                    HCN_output_filename = f"{renamed_path}{self._source}{self._version}_HCN_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                    if os.path.exists(HCN_output_filename):
                        os.remove(HCN_output_filename)
                    sh.copy(output_filename, HCN_output_filename) 
                    with nc.Dataset(HCN_output_filename, 'r+') as HCN_ds:
                        HCN_ds.variables[var_name][:, :, :] *= ( 0.003 * mw) / hcn_mw
                
                    ch3cn_mw = 41
                    CH3CN_output_filename = f"{renamed_path}{self._source}{self._version}_CH3CN_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                    if os.path.exists(CH3CN_output_filename):
                        os.remove(CH3CN_output_filename)
                    sh.copy(output_filename, CH3CN_output_filename)    
                    with nc.Dataset(CH3CN_output_filename, 'r+') as CH3CN_ds:
                        CH3CN_ds.variables[var_name][:, :, :] *= (0.002 * mw) / ch3cn_mw

                if model_var == 'pom_a4':
                    rho = 1000
                    diam = 0.134e-6
                    num_output_filename = f"{renamed_path}{self._source}{self._version}_num_{model_var}_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                    if os.path.exists(num_output_filename):
                        os.remove(num_output_filename)
                    sh.copy(output_filename, num_output_filename)
                    with nc.Dataset(num_output_filename, 'r+') as num_ds:
                        num_ds.variables[var_name][:, :, :] *= mw /mass_per_particle(rho, diam) #1.33350996e19 / 1.4
                        num_ds.variables[var_name].units = num_var_unit
                
                    svoc_mv = 310
                    SVOC_output_filename = f"{renamed_path}{self._source}{self._version}_SVOC_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                    if os.path.exists(SVOC_output_filename):
                        os.remove(SVOC_output_filename) 
                    sh.copy(output_filename, SVOC_output_filename) 
                    with nc.Dataset(SVOC_output_filename, 'r+') as SVOC_ds:
                        SVOC_ds.variables[var_name][:, :, :] *= (0.6 * mw / svoc_mv)    
            
                if model_var in ['BIGALK', 'XYLENES']:
                    #if model_var == 'BIGALK':
                        #sub_mw_mapping = {'butanes': 57.8, 'pentanes': 72, 'hexanes': 106.8, 'esters': 104.7, 'ethers': 81.5}
                    #elif model_var == 'XYLENES':   
                        #sub_mw_mapping = {'xylene': 106, 'trimethylbenzene': 120, 'other-aromatics': 126.8}
                    with nc.Dataset(output_filename, 'r+') as output:
                        for sub_var in species:
                            sub_mw = self._mw_mapping[sub_var]
                            input_ds = xr.open_dataset(f'{self._regridded_path}{self._source}_{self._original_resolution}_anthro_{sub_var}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')
                            output[var_name][:, :, :] += input_ds[var_name][:, :, :].values * (sub_mw / mw) * (unit_factor / sub_mw) * sf
                        
                if model_var == 'IVOC':
                    #sub_mw_mapping = {'C3H6': 40, 'C3H8': 44, 'C2H6': 30, 'C2H4': 28, 'BIGENE': 56, 'BIGALK': 72, 'CH3COCH3': 58, 'MEK': 72, 'CH3CHO': 44, 'CH2O': 30, 'BENZENE': 78, 'TOLUENE': 92, 'XYLENES': 106}
                    with nc.Dataset(output_filename, 'r+') as output:
                        for sub_var in species:
                            sub_mw = self._mw_mapping[sub_var]
                            input_ds = xr.open_dataset(f'{renamed_path}{self._source}{self._version}_{sub_var}_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')
                            output[var_name][:, :, :] += input_ds[var_name][:, :, :].values * (sub_mw / mw) * sf
                
                




                     



                 
                 
                 
                 
                 