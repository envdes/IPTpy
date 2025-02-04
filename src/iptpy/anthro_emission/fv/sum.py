import os
import numpy as np
import pandas as pd
import xarray as xr
import datetime

class Sum(object):
    """
    Sum class for aggregating CEDS anthropogenic emissions (monthly) before regriding.
    
    Parameters
    ----------
    input_path : str
        Path to input CEDS data.
    
    output_path : str
        Path to save the output files.
    
    start_year : int
        Starting year for processing.
    
    start_month : int
        Starting month for processing, default is 1.

    end_year : int
        Ending year for processing.
    
    end_month : int
        Ending month for processing, default is 12.

    source : str, optional
        Data source.
    
    version : str, optional
        CEDS version, either is 'v5.3' for CAMS or 'v2021-04-21' for CEDS.
    
    timestep : str, optional
        Data timestep, default is 'monthly'.
    
    original_resolution : str, optional
        Original resolution of the data, either '0.1x0.1' for CAMS or '0.5x0.5' for CEDS.
    
    target_resolution : str, optional
        Target resolution for output, default is '0.9x1.25'.
    
    var_name : str, optional
        Variable name in output files, default is 'emiss_anthro'.
    
    sourcedata_var_list: : list, optional
        List of CEDS variables to process, default is all variables.
    
    model_var_list : list, optional
        List of corresponding model variables. Automatically mapped if not provided.

    cdate : str, optional     
        Creation date for output files, default is current date.
    """
    def __init__(self,
                 input_path: str,
                 output_path: str,
                 start_year: int,
                 end_year: int,
                 start_month: int = None,
                 end_month: int = None,
                 source: str = 'CEDS',
                 version: str = 'v2021-04-21',
                 timestep: str = 'monthly',
                 original_resolution: str = '0.5x0.5',
                 target_resolution: str = '0.9x1.25',
                 var_name: str = 'emiss_anthro',
                 sourcedata_var_list: list = None,
                 model_var_list: list = None,
                 cdate: str = None):
        """
        This is the __init__ method docstring for Sum.
        """
        # Full list of CEDS variables under the PNNL DataHub portal
        full_sourcedata_var_list = ['BC', 'CO', 'NH3', 'NOx', 'OC', 'SO2',
                              'VOC01-alcohols', 'VOC02-ethane', 'VOC03-propane', 'VOC04-butanes', 
                              'VOC05-pentanes', 'VOC06-hexanes-pl', 'VOC07-ethene', 'VOC08-propene',
                              'VOC09-ethyne', 'VOC12-other-alke', 'VOC13-benzene', 'VOC14-toluene',
                              'VOC15-xylene', 'VOC16-trimethylb', 'VOC17-other-arom', 'VOC18-esters',
                              'VOC19-ethers', 'VOC21-methanal', 'VOC22-other-alka', 'VOC23-ketones',
                              'VOC24-acids']
        
        # Default to full list if var_list is not provided
        if sourcedata_var_list is None:
            sourcedata_var_list = full_sourcedata_var_list
        
        # Validate the user-provided var_list
        invalid_vars = [var for var in sourcedata_var_list if var not in full_sourcedata_var_list]
        if invalid_vars:
            raise ValueError(f"Invalid variables in var_list: {invalid_vars}. "
                             f"Valid options are: {full_sourcedata_var_list}.")    
        
        # Mapping CEDS variables to model variables
        model_mapping = {
            'BC': 'bc', 'CO': 'co', 'NH3': 'nh3', 'NOx': 'nox', 'OC': 'oc', 'SO2': 'so2',
            'VOC01-alcohols': 'alcohols', 'VOC02-ethane': 'ethane', 'VOC03-propane': 'propane',
            'VOC04-butanes': 'butanes', 'VOC05-pentanes': 'pentanes', 'VOC06-hexanes-pl': 'hexanes',
            'VOC07-ethene': 'ethene', 'VOC08-propene': 'propene', 'VOC09-ethyne': 'ethyne',
            'VOC12-other-alke': 'other-alkenes-and-alkynes', 'VOC13-benzene': 'benzene', 'VOC14-toluene': 'toluene',
            'VOC15-xylene': 'xylene', 'VOC16-trimethylb': 'trimethylbenzene', 'VOC17-other-arom': 'other-aromatics',
            'VOC18-esters': 'esters', 'VOC19-ethers': 'ethers', 'VOC21-methanal': 'methanal',
            'VOC22-other-alka': 'other-aldehydes', 'VOC23-ketones': 'ketones', 'VOC24-acids': 'acids'
        }
        
        self._input_path = input_path
        self._output_path = output_path
        self._start_year = start_year
        self._end_year = end_year
        self._source = source
        self._version = version
        self._timestep = timestep
        self._original_resolution = original_resolution
        self._target_resolution = target_resolution
        self._var_name = var_name
        self._sourcedata_var_list = sourcedata_var_list
        self._model_var_list = [model_mapping[var] for var in sourcedata_var_list if var in model_mapping]
        
        if cdate is None:
            self._cdate = datetime.datetime.now().strftime('%Y%m%d')
        else:
            self._cdate = cdate
        if source not in ['CEDS']:
            raise ValueError('source must be CEDS')   
        if target_resolution not in ['0.9x1.25']:
            raise ValueError('target_resolution must be 0.9x1.25')
        if version not in ['v2021-04-21']:
            raise ValueError('version must be v2021-04-21 for CEDS')
        if start_year > end_year:
            raise ValueError('start_year must be less than or equal to end_year')
        if start_year < 1750:
            raise ValueError('start_year must be greater than or equal to 1750')
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
        if os.path.exists(output_path) == False:
            os.makedirs(output_path)
            print(f'Created directory {output_path}')
        if os.path.exists(input_path) == False:
            raise ValueError('input_path does not exist')                
        
    
    def sum_up(self):
        """
        Sum up CEDS anthropogenic emissions (monthly) before regriding.
        """
        period_start_index = (self._start_year - 2000) * 12 + self._start_month - 1
        period_end_index = (self._end_year - 2000) * 12 + self._end_month - 1
        for source_var, model_var in zip(self._sourcedata_var_list, self._model_var_list):
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
            output_filename = f'{self._output_path}{model_var}_anthro_{self._start_year}{int(self._start_month):02d}16_{self._end_year}{int(self._end_month):02d}16_0.5_c{self._cdate}.nc'
            if os.path.exists(output_filename):
                os.remove(output_filename)
            renamed_da = ds_var_period[varname].sum(dim='sector').rename(self._var_name)
            renamed_da.attrs['long_name'] = ds_var_period[varname].attrs['long_name']
            renamed_da.attrs['units'] = ds_var_period[varname].attrs['units']
            renamed_da.attrs['cell_methods'] = ds_var_period[varname].attrs['cell_methods']
            renamed_da.to_netcdf(output_filename)
            print(f'Saved {output_filename}')
            # special handling for SO2 emissions (individual sectors)
            if source_var == 'SO2':
                print('Saving individual sector files for SO2')
                sector_list = ['agr', 'ene', 'ind', 'tra', 'res', 'sol', 'was', 'shp']
                for i, sector in enumerate(sector_list):
                    output_filename = f'{self._output_path}{model_var}_{sector}_anthro_{self._start_year}{int(self._start_month):02d}16_{self._end_year}{int(self._end_month):02d}16_0.5_c{self._cdate}.nc'
                    if os.path.exists(output_filename):
                        os.remove(output_filename)
                    renamed_da = ds_var_period[varname].sel(sector=i).rename(self._var_name)
                    renamed_da.attrs['long_name'] = ds_var_period[varname].attrs['long_name']
                    renamed_da.attrs['units'] = ds_var_period[varname].attrs['units']
                    renamed_da.attrs['cell_methods'] = ds_var_period[varname].attrs['cell_methods']
                    renamed_da.to_netcdf(output_filename)  


                 
                 
                 
                 
                 