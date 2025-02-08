from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 2 - Pre-Alpha",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering :: Atmospheric Science",
    ]

with open("README.md", "r", encoding="utf-8") as fp:
    long_description = fp.read()

setup(
    name="iptpy",
    version="0.0.0",
    author="Yuan Sun",
    author_email="sunyuanzju@outlook.com",
    url="https://github.com/envdes/IPTpy",
    description="ipypy is a Python-based tool designed to process input data for CESM.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="MIT",
    classifiers=classifiers,
    install_requires=['numpy', 'pandas', 'xarray', 'datetime', 'esmpy', 'xesmf', 'netCDF4'],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    )