# Installation
Below are installation instructions for setting up via the command line in a bash environment. You can choose to manage the environment using either [venv (Python virtual environment)](https://docs.python.org/3/library/venv.html) or [Conda](https://docs.conda.io/projects/conda/en/latest/).

## Quick Installation

- Method1: Install IPTpy by [pip](https://pypi.org/project/pip/).

```bash
pip install iptpy
```

- Method2: Install IPTpy by Conda.

```bash
conda install -c conda-forge iptpy
```

## Installation Step by Step

### Step 1: Check the Python path and virtual environment

- Check the Python path.

```bash
which python3
```

- List and choose an existing virtual environment for installation.

```bash
# choose an virtual environment in a specific folder
ls /path/to/venvs

# or list Conda virtual environment and choose one
conda env list
```

- Or, create a new virtual environment for installation. 

```bash
# for example, 'myenv' is the new virtual environment name
python3 -m venv myenv 

# or specify Python version when creating a new virtual environment
python3.9 -m venv myenv

# or create a Conda virtual environment
conda create -n myenv

# or create a Conda virtual environment with a specific version of Python
conda create -n myenv python=3.9

# or create a Conda virtual environment with a specific version of Python and packages
conda create -n myenv python=3.9 -c conda-forge numpy xarray pandas datetime netcdf4 esmpy xesmf iptpy
```

### Step 2: Install IPTpy

- Install IPTpy in a venv virtual environment.

```bash
source myenv/bin/activate
pip install iptpy 
```

- Install IPTpy in a Conda virtual environment.

```bash
conda activate myenv
conda install -c conda-forge iptpy
```

### Step 3: Verify installation

- Verify installation in a venv virtual environment.

```bash
pip show iptpy
```

- Verify installation in a Conda virtual environment.

```bash
conda list iptpy
```

### Step 4: Deactivation

- Deactivate venv virtual environment after installation.

```bash
deactivate
```

- Deactivate Conda virtual environment after installation. 

```bash
conda deactivate
```

# Environment 

## Requirement

IPTpy requires seven libraries for its functionality. 

- [numpy](https://numpy.org/): A fundamental package for scientific computing with Python.
- [xarray](https://xarray.dev/): Working with labeled arrays and datasets.
- [pandas](https://pandas.pydata.org/): A data analysis and manipulation tool.
- [netcdf4](https://unidata.github.io/netcdf4-python/#netCDF4): A Python interface to the netCDF C library. 
- [esmpy](https://earthsystemmodeling.org/esmpy/): ESMF Python regridding interface. 
- [xesmf](https://xesmf.readthedocs.io/en/latest/#): Universal regridder for geospatial data. 

For reference, the following version setup works: numpy=2.0.2, xarray=2024.7.0, pandas=2.2.3, netcdf4=1.7.1, esmfpy=8.6.1, xesmf=0.8.7. Specifying versions during installation as follow:

```bash
# using pip
pip install numpy==2.0.2 xarray==2024.7.0 pandas==2.2.3 netCDF4==1.7.1 esmpy==8.6.1 xesmf==0.8.7

# using conda
conda install -c conda-forge numpy=2.0.2 xarray=2024.7.0 pandas=2.2.3 netCDF4=1.7.1 esmpy=8.6.1 xesmf=0.8.7
```



## Error (selected)

Errors may occur during library installation, such as package incompatibility or dependency conflicts. 

**error1**: 

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



**error2** 

ERROR: Could not find a version that satisfies the requirement esmpy (from iptpy) (from versions: none)
ERROR: No matching distribution found for esmpy

**note**: esmpy is not distributed through the Python Package Index (PyPI), so you won’t be able to install it via pip install esmpy unless it’s available from another source.

```bash
conda install -c conda-forge esmpy
```

