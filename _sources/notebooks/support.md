# Support

Encountered an error? No worries. Errors are opportunities for learning and progress. 

## Errors During Installation

Errors may occur during library installation, such as package incompatibility or dependency conflicts. 

### **error1**

```
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[9], line 1
----> 1 import xesmf as xe
      2 print("XESMF version:", xe.__version__)

File ~/miniconda3/envs/testingenv/lib/python3.11/site-packages/xesmf/__init__.py:4
      1 # flake8: noqa
      3 from . import data, util
----> 4 from .frontend import Regridder, SpatialAverager
      6 try:
      7     from ._version import __version__

File ~/miniconda3/envs/testingenv/lib/python3.11/site-packages/xesmf/frontend.py:9
      7 import cf_xarray as cfxr
      8 import numpy as np
----> 9 import sparse as sps
     10 import xarray as xr
     11 from shapely.geometry import LineString

File ~/miniconda3/envs/testingenv/lib/python3.11/site-packages/sparse/__init__.py:77
     74 from numpy import power as pow
     75 from numpy import right_shift as bitwise_right_shift
---> 77 from ._common import (
     78     SparseArray,
...
     56     ]:
---> 57         ufunc.__module__ = "numpy.strings"
     58         ufunc.__qualname__ = ufunc.__name__

AttributeError: 'numpy.ufunc' object has no attribute '__module__'
```

**note**: AttributeError: 'numpy.ufunc' object has no attribute '__module__', is likely due to an incompatibility between xesmf and your version of numpy. This issue can occur when a library is trying to use an outdated or unsupported feature in a newer version of numpy.

**solution**: conda install numpy==**2.0.2**. After reinstalling numpy, remember to restart the kernel. 

### **error2** 

ERROR: Could not find a version that satisfies the requirement esmpy (from iptpy) (from versions: none)
ERROR: No matching distribution found for esmpy

**note**: esmpy is not distributed through the Python Package Index (PyPI), so you won’t be able to install it via `pip install esmpy` unless it’s available from another source.

```bash
conda install -c conda-forge esmpy
```



## Errors During Input Processing

During input processing, carefully read any errors or warnings for helpful hints. You will become more familiar with IPTpy through practice. Make full use of [Issues](https://github.com/envdes/IPTpy/issues) and [Discussions](https://github.com/envdes/IPTpy/discussions) to find solutions. 

### Frequent Questions

- To be added. 

## Errors During Simulations

If you have processed input data and used it in CESM, errors may also occur during simulation. For troubleshooting, follow these steps:

- **Verify default input data first:** Before using customized input data, ensure that CESM job scripts run successfully with the default input data. This helps isolate potential errors caused by modifications. If issues are unrelated to input data, refer to the [DiscussCESM Forums](https://bb.cgd.ucar.edu/cesm/) for support.

- **Understand Emission Input Interpolation**: Some emission datasets, such as CEDS, provide data on the 16th of each month. If a simulation starts on **01 Jan 2015**, the input dataset must include data from **16 Dec 2014** to enable interpolation between **16 Dec 2014 and 16 Jan 2015**. Similarly, if a simulation extends to the **end of 2015**, the input must include **16 Jan 2016** to interpolate emissions from **16 Dec 2015 to 16 Jan 2016**.

### Error Cases (Selected)

**error1**: *imp_sol: step failed to converge @ (lchnk,vctrpos,nstep,dt,time) =     1281     431       1   11.25000       22.50000* 

**notes**: If the simulation stops due to CAM failing to converge, it likely indicates an issue with the input data, such as missing values (fill values) instead of actual data.
