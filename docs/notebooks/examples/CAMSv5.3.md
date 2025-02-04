# CAMSv5.3

This Python script is used to process CAMSv5.3 data using IPTpy. Users could use [Jupyter Notebook](https://jupyter.org/) to taste the code. 

```python
import libraries
import xarray as xr
import numpy as np
from iptpy.anthro_emission.fv import sum, regrid, rename
```

## Step1: Regrid from 0.1°x0.1° to 0.9°x1.25°

```python
regrid_instance = regrid(
    input_path='/gws/nopw/j04/duicv/yuansun/dataset/CAMS/CAMS-GLOB-ANT_v5.3/',
    output_path='/gws/nopw/j04/duicv/yuansun/IPTpy/tests/regrid/',
    regridder_filename = '/gws/nopw/j04/duicv/yuansun/IPTpy/tests/regrid/test_cams_0.1x0.1_0.9x1.25_regridder.nc',
    start_year=2018,
    end_year=2018,
    source='CAMS-GLOB-ANT',
    version='v5.3'
)
regrid_instance.generate_regridder()
regrid_instance.apply_regridder()
```

- Once a regridder exists, it can be reused and does not need to be generated when running apply_regridder() multiple times.

 ## Step2: Rename gridded data

```python
rename_instance = rename(
    input_path='/gws/nopw/j04/duicv/yuansun/IPT-py/tests/regrid/',
    output_path='/gws/nopw/j04/duicv/yuansun/IPT-py/tests/rename/',
    start_year=2018,
    end_year=2018,
    source='CAMS-GLOB-ANT',
    version='v5.3'
)
rename_instance.rename()
```

- Note that files in the output_path will be automatically deleted before new files are generated, so manual deletion is not required.
