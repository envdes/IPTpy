import os
import numpy as np
import pandas as pd
import xarray as xr
import datetime
import netCDF4 as nc
import shutil as sh

class Rename(object):
    """
    Rename class for renaming gridded CAMS or CEDS emissions to match the model inputs.

    Parameters
    ----------
    input_path : str
        Path to input CAMS or CEDS regrided data.

    output_path : str
        Path to save the output files for CESM simulation.     

    start_year : int       
        Starting year for processing.

    end_year : int
        Ending year for processing.

    source : str        
        Data source, either 'CAMS-GLOB-ANT' or 'CEDS'.

    version : str, optional        
        Version of the data source, either 'v5.3' for CAMS-GLOB-ANT or 'v2021-04-21' for CEDS.

    original_resolution : str, optional    
        Original resolution of the data source, either '0.1x0.1' for CAMS-GLOB-ANT or '0.5x0.5' for CEDS.

    cdate : str, optional    
        Creation date for output files, default is current date.

    timestep : str, optional
        Data timestep, default is 'monthly'.

    target_resolution : str, optional
        Target resolution for output, default is '0.9x1.25'.    

    target_lat : list, optional    
        Target latitude values. Uses default values if not specified. 

    target_lon : list, optional
        Target longitude values. Uses default values if not specified.

    var_namelist : list, optional
        List of variables to process, default is all variables.

    model_var_list : list, optional            
        List of corresponding model variables. Automatically mapped if not provided.

    mw_list : list, optional    
        List of molecular weights for each variable. Automatically mapped if not provided.

    sf_list : list, optional    
        List of scale factors for each variable. Automatically mapped if not provided.
    """ 
    def __init__(self,
                 input_path: str,
                 output_path: str,
                 start_year: int,
                 end_year: int,
                 source: str,
                 version: str = None,
                 start_month: int = None,
                 end_month: int = None,
                 original_resolution: str = None,
                 cdate: str = None,
                 timestep: str = 'monthly',
                 target_resolution: str = '0.9x1.25',
                 target_lat: list = None,
                 target_lon: list = None,
                 var_namelist: list = None,
                 model_var_list: list = None,
                 mw_list: list = None,
                 sf_list: list = None):
        """
        This is the __init__ method docstring for Rename.
        """

        self._source = source
        self._target_lat = target_lat
        self._target_lon = target_lon
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
            elif source == 'CEDS':
                version = 'v2021-04-21'
              
        self._version = version   
        if original_resolution is None:
            if self._source == 'CAMS-GLOB-ANT':
                original_resolution = '0.1x0.1'
            elif self._source == 'CEDS':
                original_resolution = '0.5x0.5'
        self._original_resolution = original_resolution

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

        if self._source == 'CAMS-GLOB-ANT':
            first_year = 2000
            last_year = datetime.datetime.now().year - 1
            if version not in ['v5.3']:
               raise ValueError('version must be v5.3 for CAMS-GLOB-ANT') 
            if original_resolution not in ['0.1x0.1']:
               raise ValueError('original_resolution must be 0.1x0.1 for CAMS-GLOB-ANT')
        elif self._source == 'CEDS':
            first_year = 1750
            last_year = 2020
            if version not in ['v2021-04-21']:
               raise ValueError('version must be v2021-04-21 for CEDS')
            if original_resolution not in ['0.5x0.5']:
               raise ValueError('original_resolution must be 0.5x0.5 for CEDS')
            if end_year > 2020:
               raise ValueError('end_year must be less than or equal to 2020 for CEDS')
        
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
        if start_year < first_year:
            raise ValueError('start_year must be greater than or equal to ' + str(first_year))
        if end_year > last_year:
               raise ValueError('end_year must be less than or equal to ' + str(last_year))      
        full_var_namelist = ['bc_a4', 'CO', 'NH3', 'NO', 'pom_a4', 'SO2', 
                               'C2H6', 'C3H8', 'C2H4', 'C3H6', 'C2H2', 'BIGENE', 
                               'BENZENE', 'TOLUENE', 'CH2O', 'CH3CHO', 'BIGALK', 'XYLENES', 
                               'CH3OH', 'C2H5OH', 'CH3COCH3', 'MEK', 'HCOOH',
                               'CH3COOH', 'IVOC']
        model_var_mapping = {'bc_a4': 'bc', 'CO': 'co', 'NH3': 'nh3', 'NO': 'nox', 'pom_a4': 'oc', 'SO2': 'so2', 
                             'C2H6': 'ethane', 'C3H8': 'propane', 'C2H4': 'ethene', 'C3H6': 'propene', 'C2H2': 'ethyne', 'BIGENE': 'other-alkenes-and-alkynes', 
                             'BENZENE': 'benzene', 'TOLUENE': 'toluene', 'CH2O': 'methanal', 'CH3CHO': 'other-aldehydes',
                             'BIGALK': ["butanes","pentanes","hexanes","esters","ethers"], 
                             'XYLENES': ['xylene', 'trimethylbenzene', 'other-aromatics'], 
                             'CH3OH': 'alcohols', 'C2H5OH': 'alcohols', 'CH3COCH3': 'ketones', 'MEK': 'ketones', 'HCOOH': 'acids',
                             'CH3COOH': 'acids', 'IVOC': ['C3H6', 'C3H8', 'C2H6', 'C2H4', 'BIGENE', 'BIGALK', 'CH3COCH3', 'MEK', 'CH3CHO', 'CH2O', 'BENZENE', 'TOLUENE', 'XYLENES']}                       
        mw_mapping = {'bc_a4': 12, 'CO': 28, 'NH3': 17, 'NO': 30, 'pom_a4': 12, 'SO2': 64,
                      'C2H6': 30, 'C3H8': 44, 'C2H4': 28, 'C3H6': 40, 'C2H2': 26, 'BIGENE': 56, 
                      'BENZENE': 78, 'TOLUENE': 92, 'CH2O': 30, 'CH3CHO': 44, 'BIGALK': 72, 'XYLENES': 106, 
                      'CH3OH': 32, 'C2H5OH': 46, 'CH3COCH3': 58, 'MEK': 72, 'HCOOH': 46, 
                      'CH3COOH': 60, 'IVOC': 184}
        sf_mapping = {'bc_a4': 1, 'CO': 1, 'NH3': 1, 'NO': 46/30, 'pom_a4': 1.4, 'SO2': 1,
                      'C2H6': 1, 'C3H8': 1, 'C2H4': 1, 'C3H6': 1, 'C2H2': 1, 'BIGENE': 1, 
                      'BENZENE': 1, 'TOLUENE': 1, 'CH2O': 1, 'CH3CHO': 1, 'BIGALK': 1, 'XYLENES': 1, 
                      'CH3OH': 0.15, 'C2H5OH': 0.85, 'CH3COCH3': 0.2, 'MEK': 0.8, 'HCOOH': 0.5, 
                      'CH3COOH': 0.5, 'IVOC': 0.2}
        if var_namelist is None:
            self._var_namelist = full_var_namelist  
        else:
            self._var_namelist = var_namelist
        invalid_vars = [var for var in self._var_namelist if var not in full_var_namelist]
        if invalid_vars:
            raise ValueError(f"Invalid variables in model_var_list: {invalid_vars}. "
                             f"Valid options are: {full_var_namelist}.")  
        required_sub_vars = {'C3H6', 'C3H8', 'C2H6', 'C2H4', 'BIGENE', 'BIGALK', 
                    'CH3COCH3', 'MEK', 'CH3CHO', 'CH2O', 'BENZENE', 'TOLUENE', 'XYLENES'}
        if 'IVOC' in self._var_namelist and not any(var in self._var_namelist for var in required_sub_vars):
            missing_vars = required_sub_vars - set(var_namelist)
            print(f"IVOC is present in var_namelist but the following required sub-variables are missing: {missing_vars}. "
                     f"IVOC requires all of the following: {required_sub_vars}")
        
        self._model_var_list = [model_var_mapping[var] for var in self._var_namelist]
        self._mw_list = [mw_mapping[var] for var in self._var_namelist]
        self._sf_list = [sf_mapping[var] for var in self._var_namelist]

    def rename(self):
        """
        Rename the emissions files to match the model inputs.
        """
        time_units = "days since 2000-01-01 00:00:00"
        var_name = 'emiss_anthro'
        var_unit = 'molecules/cm2/s'
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

        for varname, model_var, mw, sf in zip(self._var_namelist, self._model_var_list, self._mw_list, self._sf_list):
            print(f'Renaming {varname}')
            output_filename = f"{self._output_path}{self._source}{self._version}_{varname}_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
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
                if isinstance(model_var, list):
                    output.variables[var_name][:, :, :] = 0
                else:    
                    input_ds = xr.open_dataset(f'{self._input_path}{self._source}_{self._original_resolution}_anthro_{model_var}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')
                    output.variables[var_name][:, :, :] = input_ds[var_name][:, :, :].values * (unit_factor / mw) * sf
                
            if varname == 'bc_a4':
                rho = 1700
                diam = 0.134e-6
                num_output_filename = f"{self._output_path}{self._source}{self._version}_num_{varname}_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                if os.path.exists(num_output_filename):
                    os.remove(num_output_filename)
                sh.copy(output_filename, num_output_filename)
                with nc.Dataset(num_output_filename, 'r+') as num_ds:
                     num_ds.variables[var_name][:, :, :] *= mw /mass_per_particle(rho, diam) #5.60298303e18 
            
            if varname == 'CO':
                hcn_mw = 27
                HCN_output_filename = f"{self._output_path}{self._source}{self._version}_HCN_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                if os.path.exists(HCN_output_filename):
                    os.remove(HCN_output_filename)
                sh.copy(output_filename, HCN_output_filename) 
                with nc.Dataset(HCN_output_filename, 'r+') as HCN_ds:
                    HCN_ds.variables[var_name][:, :, :] *= ( 0.0055 * mw) / hcn_mw
                
                ch3cn_mw = 41
                CH3CN_output_filename = f"{self._output_path}{self._source}{self._version}_CH3CN_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                if os.path.exists(CH3CN_output_filename):
                    os.remove(CH3CN_output_filename)
                sh.copy(output_filename, CH3CN_output_filename)    
                with nc.Dataset(CH3CN_output_filename, 'r+') as CH3CN_ds:
                    CH3CN_ds.variables[var_name][:, :, :] *= (0.0025 * mw) / ch3cn_mw

            if varname == 'pom_a4':
                rho = 1000
                diam = 0.134e-6
                num_output_filename = f"{self._output_path}{self._source}{self._version}_num_{varname}_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                if os.path.exists(num_output_filename):
                    os.remove(num_output_filename)
                sh.copy(output_filename, num_output_filename)
                with nc.Dataset(num_output_filename, 'r+') as num_ds:
                    num_ds.variables[var_name][:, :, :] *= mw /mass_per_particle(rho, diam) #1.33350996e19 / 1.4
                
                svoc_mv = 310
                SVOC_output_filename = f"{self._output_path}{self._source}{self._version}_SVOC_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                if os.path.exists(SVOC_output_filename):
                    os.remove(SVOC_output_filename) 
                sh.copy(output_filename, SVOC_output_filename) 
                with nc.Dataset(SVOC_output_filename, 'r+') as SVOC_ds:
                    SVOC_ds.variables[var_name][:, :, :] *= (0.6 * mw / svoc_mv)    
            
            if varname == 'SO2':
                rho = 1770
                mw2 = 115
                if self._source == 'CAMS-GLOB-ANT':
                    ag_sol_was = ['awb', 'fef', 'swd']
                    res_tra = ['res', 'tro', 'tnr']
                    ene_ind = ['ene', 'ind', 'ref']
                elif self._source == 'CEDS':
                    ag_sol_was = ['agr', 'sol', 'was']
                    res_tra = ['res', 'tra']
                    ene_ind = ['ene', 'ind']
                shp = ['shp']

                SO2_anthro_ag_ship_res_filename = f"{self._output_path}{self._source}{self._version}_{varname}_anthro-ag-ship-res_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                SO2_anthro_ene_filename = f"{self._output_path}{self._source}{self._version}_{varname}_anthro-ene_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                so4_a1_anthro_ag_ship_filename = f"{self._output_path}{self._source}{self._version}_so4_a1_anthro-ag-ship_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                so4_a2_anthro_res_filename = f"{self._output_path}{self._source}{self._version}_so4_a2_anthro-res_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                so4_a1_anthro_ene_vertical_filename = f"{self._output_path}{self._source}{self._version}_so4_a1_anthro-ene-vertical_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                num_so4_a1_anthro_ag_ship_filename = f"{self._output_path}{self._source}{self._version}_num_so4_a1_anthro-ag-ship_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                num_so4_a2_anthro_res_filename = f"{self._output_path}{self._source}{self._version}_num_so4_a2_anthro-res_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
                num_so4_a1_anthro_ene_vertical_filename = f"{self._output_path}{self._source}{self._version}_num_so4_a1_anthro-ene-vertical_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc"
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
                                    ds_so2 = xr.open_dataset(f'{self._input_path}{self._source}_{self._original_resolution}_anthro_{model_var}_{s}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')
                                    so2_var[:, :, :] += ds_so2[var_name].values * 0.975 * ( unit_factor / mw )
  
                        if file == SO2_anthro_ene_filename:
                            var_name4 = 'emiss_ene_ind'
                            new_var4 = output.createVariable(var_name4, 'f4', ('time', 'lat', 'lon'))
                            new_var4.units = var_unit
                            new_var4[:, :, :] = 0.0
                            for s in ene_ind:
                                ds_so2 = xr.open_dataset(f'{self._input_path}{self._source}_{self._original_resolution}_anthro_{model_var}_{s}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')
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
                                    ds_so2 = xr.open_dataset(f'{self._input_path}{self._source}_{self._original_resolution}_anthro_{model_var}_{s}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')
                                    so2_var[:, :, :] += ds_so2[var_name].values * 0.975 * ( unit_factor / mw )
                       
                        if file == so4_a2_anthro_res_filename:    
                            var_name4 = 'emiss_res_tran'
                            new_var4 = output.createVariable(var_name4, 'f4', ('time', 'lat', 'lon'))
                            new_var4.units = var_unit
                            new_var4[:, :, :] = 0.0
                            for s in res_tra:
                                ds_so2 = xr.open_dataset(f'{self._input_path}{self._source}_{self._original_resolution}_anthro_{model_var}_{s}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')
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
                                ds_so2 = xr.open_dataset(f'{self._input_path}{self._source}_{self._original_resolution}_anthro_{model_var}_{s}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')                    
                                layer_values = np.zeros_like(ds_so2[var_name].values)
                                layer_values += ds_so2[var_name].values * 0.025 * ( unit_factor / mw ) / 2e4
                            new_var4[:, 3:7, :, :] = layer_values[:, np.newaxis, :, :]
                
                if os.path.exists(num_so4_a1_anthro_ag_ship_filename):
                    os.remove(num_so4_a1_anthro_ag_ship_filename)
                sh.copy(so4_a1_anthro_ag_ship_filename, num_so4_a1_anthro_ag_ship_filename)
                with nc.Dataset(num_so4_a1_anthro_ag_ship_filename, 'r+') as input_ds:
                    input_ds['emiss_ag_sol_was'][:, :, :] *= mw2 /mass_per_particle(rho, 0.134e-6) #diam = 0.134e-6, 5.157170449543804e19
                    input_ds['emiss_ship'][:, :, :] *= mw2 /mass_per_particle(rho, 0.261e-6) #diam = 0.261e-6, 6.979181393389552e18   
                
                if os.path.exists(num_so4_a2_anthro_res_filename):
                    os.remove(num_so4_a2_anthro_res_filename)   
                sh.copy(so4_a2_anthro_res_filename, num_so4_a2_anthro_res_filename)     
                with nc.Dataset(num_so4_a2_anthro_res_filename, 'r+') as input_ds:
                    input_ds['emiss_res_tran'][:, :, :] *= mw2 /mass_per_particle(rho, 0.0504e-6) #diam = 0.0504e-6, 9.692466974041687e20   
                
                if os.path.exists(num_so4_a1_anthro_ene_vertical_filename):
                    os.remove(num_so4_a1_anthro_ene_vertical_filename)
                sh.copy(so4_a1_anthro_ene_vertical_filename, num_so4_a1_anthro_ene_vertical_filename)    
                with nc.Dataset(num_so4_a1_anthro_ene_vertical_filename, 'r+') as input_ds:  
                    input_ds['emiss_ene_ind'][:, :, :, :] *= mw2 /mass_per_particle(rho, 0.261e-6) #diam = 0.261e-6, 6.979181393389552e18   
            
            if varname in ['BIGALK', 'XYLENES']:
                if varname == 'BIGALK':
                    sub_mw_mapping = {'butanes': 57.8, 'pentanes': 72, 'hexanes': 106.8, 'esters': 104.7, 'ethers': 81.5}
                elif varname == 'XYLENES':   
                    sub_mw_mapping = {'xylene': 106, 'trimethylbenzene': 120, 'other-aromatics': 126.8}
                with nc.Dataset(output_filename, 'r+') as output:
                    for sub_var in model_var:
                        sub_mw = sub_mw_mapping[sub_var]
                        input_ds = xr.open_dataset(f'{self._input_path}{self._source}_{self._original_resolution}_anthro_{sub_var}_{self._version}_{self._timestep}_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')
                        output[var_name][:, :, :] += input_ds[var_name][:, :, :].values * (sub_mw / mw) * (unit_factor / sub_mw) * sf
                        
            if varname == 'IVOC':
                sub_mw_mapping = {'C3H6': 40, 'C3H8': 44, 'C2H6': 30, 'C2H4': 28, 'BIGENE': 56, 'BIGALK': 72, 'CH3COCH3': 58, 'MEK': 72, 'CH3CHO': 44, 'CH2O': 30, 'BENZENE': 78, 'TOLUENE': 92, 'XYLENES': 106}
                with nc.Dataset(output_filename, 'r+') as output:
                    for sub_var in model_var:
                        sub_mw = sub_mw_mapping[sub_var]
                        input_ds = xr.open_dataset(f'{self._output_path}{self._source}{self._version}_{sub_var}_anthro_{self._start_year}{int(self._start_month):02d}{date}_{self._end_year}{int(self._end_month):02d}{date}_{self._target_resolution}_c{self._cdate}.nc')
                        output[var_name][:, :, :] += input_ds[var_name][:, :, :].values * (sub_mw / mw) * sf
                
                




