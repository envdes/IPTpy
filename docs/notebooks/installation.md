# Installation
Below are installation instructions for setting up via the command line in a bash environment. We recommend managing the environment using [Conda](https://docs.conda.io/projects/conda/en/latest/).

## Quick Installation

In case all required packages are already installed in a certain Conda virtual environment, install IPTpy directly using the methods below. 

- Method1: Install IPTpy by [pip](https://pypi.org/project/pip/).

```bash
pip install iptpy
```

- Method2: Install IPTpy by Conda.

```bash
conda install -c conda-forge iptpy
```

- Method3: Install IPTpy by clone

```bash
git clone https://github.com/envdes/IPTpy.git
cd IPTpy
pip install .
```



## Installation Step by Step

Otherwise, create a new virtual environment and install required packages and IPTpy step by step. 

### Step 1: Check the Python path and virtual environment

- Check the Python path.

```bash
which python3
```

- List and choose an existing virtual environment for installation.

```bash
# list Conda virtual environment and choose one
conda env list
```

- Or, create a new virtual environment for installation. 

```bash
# create a Conda virtual environment
conda create -n myenv

# or create a Conda virtual environment with a specific version of Python
conda create -n myenv python=3.9

# or create a Conda virtual environment with a specific version of Python and packages
conda create -n myenv python=3.9 -c conda-forge numpy xarray pandas datetime netcdf4 esmpy xesmf

# or create a Conda virtual environment with required packages using .yml
conda env create -n myenv -f requirements.yml
```

### Step 2: Install IPTpy

- Install IPTpy in a Conda virtual environment.

```bash
conda activate myenv
conda install -c conda-forge iptpy
```

### Step 3: Verify installation

- Verify installation in a Conda virtual environment.

```bash
conda list iptpy
```

### Step 4: Deactivation

- Deactivate Conda virtual environment after installation. 

```bash
conda deactivate
```

# Environment 

## Requirement

IPTpy requires seven packages for its functionality. 

- [numpy](https://numpy.org/): A fundamental package for scientific computing with Python.
- [xarray](https://xarray.dev/): Working with labeled arrays and datasets.
- [pandas](https://pandas.pydata.org/): A data analysis and manipulation tool.
- [netcdf4](https://unidata.github.io/netcdf4-python/#netCDF4): A Python interface to the netCDF C library. 
- [esmpy](https://earthsystemmodeling.org/esmpy/): ESMF Python regridding interface. 
- [xesmf](https://xesmf.readthedocs.io/en/latest/#): Universal regridder for geospatial data. 

For reference, the following version setup works: numpy=2.0.2, xarray=2024.7.0, pandas=2.2.3, netcdf4=1.7.1, esmfpy=8.6.1, xesmf=0.8.7. Specifying versions during installation as follow:

```bash
# using conda
conda install -c conda-forge numpy=2.0.2 xarray=2024.7.0 pandas=2.2.3 netCDF4=1.7.1 esmpy=8.6.1 xesmf=0.8.7
```
