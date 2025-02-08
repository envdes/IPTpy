# CAMSv5.3

This Python script is used to process CAMSv5.3 data using IPTpy. Users could use [Jupyter Notebook](https://jupyter.org/) to taste the code. 

```python
# import packages
import libraries
import xarray as xr
import numpy as np
from iptpy.anthro_emission.fv import FV
```

```python
# initialize
fv_instance = FV(
  preregrid_path='/gws/nopw/j04/duicv/yuansun/dataset/CAMS/CAMS-GLOB-ANT_v5.3/',
  regridder_filename='/gws/nopw/j04/duicv/yuansun/IPTpy/tests/regridded/test_cams_0.1x0.1_0.9x1.25_regridder.nc',
    regridded_path='/gws/nopw/j04/duicv/yuansun/IPTpy/tests/regridded/',
    start_year=2018,
    end_year=2018,
    source='CAMS-GLOB-ANT',
    version='v5.3',
    original_resolution='0.1x0.1',
)
```

## Step1: Regrid from 0.1°x0.1° to 0.9°x1.25°

```python
fv_instance.generate_regridder()
fv_instance.apply_regridder()
```

- Once a regridder exists, it can be reused and does not need to be generated when running apply_regridder() multiple times.

 ## Step2: Rename gridded data

```python
fv_instance.rename('/gws/nopw/j04/duicv/yuansun/IPTpy/tests/renamed/')
```

- Note that files in the output_path will be automatically deleted before new files are generated, so manual deletion is not required.
