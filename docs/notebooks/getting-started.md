# Overview

IPTpy enables users to generate global anthropogenic emissions from [Copernicus Atmosphere Monitoring Service (CAMS)](https://atmosphere.copernicus.eu) or [Community Emissions Data System (CEDS)](https://www.pnnl.gov/projects/ceds) inventories for the finite volume dynamic core (FV dycore), covering the most recent historical data. Compared to the original, IPTpy offers greater flexibility by allowing users to generate specific species and specify data on a monthly basis. 

## Why IPTpy?

| Feature                                    | [IPT](https://github.com/NCAR/IPT)                           | [IPTpy](https://github.com/envdes/IPTpy)                     |
| ------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Function                                   | Processing anthropogenic and biomass emission for FV and spectral element (SE) dycores. | Processing anthropogenic emissions for FV dycores.           |
| Supported global anthropogenic inventories | [CAMSv4.2](https://ads.atmosphere.copernicus.eu/datasets/cams-global-emission-inventories?tab=overview), [CEDSv2017_05_18](https://doi.org/10.5194/gmd-11-369-2018) | [CAMv5.3](https://permalink.aeris-data.fr/CAMS-GLOB-ANT), [CEDSv2021_04_21](https://data.pnnl.gov/dataset/CEDS-4-21-21) |
| Supported global biomass inventories       | [FINN](https://www2.acom.ucar.edu/modeling/finn-fire-inventory-ncar), [QFED](https://gmao.gsfc.nasa.gov/research/science_snapshots/global_fire_emissions.php#:~:text=The%20Quick%20Fire%20Emissions%20Dataset%20%28QFED%29%20was%20developed,Observing%20System%20%28GEOS%29%20modeling%20and%20data%20assimilation%20systems.) | Not applicable                                               |
| Species                                    | Generates all species by default (no user selection).        | Allows users to select specific species as needed.           |
| Period                                     | Selected by year(s).                                         | Selected by year(s) and months                               |

- While IPT-py does not yet replicate all IPT functionalities, contributions are welcome to enhance its capabilities further.

## Acknowledgment

This work used the [ARCHER2 UK National Supercomputing Service](https://www.archer2.ac.uk) and [JASMIN, the UK’s collaborative data analysis environment](https://www.jasmin.ac.uk).
