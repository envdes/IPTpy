# Support

Encountered an error? No worries. Errors are opportunities for learning and progress. 

## Errors During the Input Processing

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
