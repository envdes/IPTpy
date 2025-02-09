# Understand the Process

## Sum

CESM requires summed values for most species, except for sulfate, which is sector-specific. The `FV.sum_up` function allows users to aggregate the **CEDS data downloaded via Globus**. The download data is stored in `input_path` and the aggregated data is saved in `preregrid_path` for subsequent processing. In contrast, data obtained using Wget is already pre-summed. 

## Regrid

Consistent with IPT, we use the **conservative** regridding algorithm from ESMF. For a detailed explanation, refer to the [ESMF Regridding methods](https://earthsystemmodeling.org/regrid/#regridding-methods). To regrid emission data from high to low spatial resolution, `FV.generate_regridder` creates a regridder, which is automatically saved as `regridder_filename`. Then, `FV.apply_regridder` applies the regridder to data stored in `preregrid_path` and saves the output in `regridded_path`. Notably,`FV.apply_regridder` regrids salfate emission by sectors, while all other species are processed as summed values. 

## Rename

`FV.rename` convert emission from the original unit $kg/m^2 s$ to $\text{molecules}/{cm}^2~s$ based on the **Equation 1**: 

$$
E_{converted} = E_{original} \times \frac{N_A}{M} \times \frac{10^3}{10^4}, \tag{1}
$$

where $E_{\text{original}}$ is the emission in $kg/ m^{2}~ s$, $E_{\text{converted}}$ is the emission in $\text{molecules}/cm^{2} ~s$, $N_A$ is Avogadro’s number ($6.022 \times 10^{23}$ molecules/mol), $M$ is the molecular weight of the species in g/mol, $10^3$ accounts for the unit conversion from $kg$ to $g$, $10^4$ accounts for the unit conversion from $m^2$ to ${cm}^2$ . 

Besides, scale factors are applied to adjust emissions based on specific assumptions or corrections. These factors can account for uncertainties, regional variations, or improvements in emission estimates (**Equation 2**):

$$
E_{scaled} = E_{converted} \times \textrm{SF}, \tag{2}
$$

where  $E_{\text{scaled}}$ is the adjusted emission, $E_{\text{converted}}$ is the emission converted from the original unit, $\text{SF}$ is the scale factor, which varies based on species, regions, or datasets. **Table 1** list the default $M$ and $SF$ that `FV.rename` automatically assigns based on the `model_var_list`. Users can also specify custom values using `mw_mapping` and `sf_mapping`. 

***Table 1** Lists of molecular weight ($M$) and scale factors ($\text{SF}$)*.

| Variable name    | Molecular weight ($M$) | Scale factor ($\text{SF}$) |
| ---------------- | ---------------------- | -------------------------- |
| bc_a4[^1]        | 12                     | 1                          |
| CO               | 28                     | 1                          |
| NH3              | 17                     | 1                          |
| NO               | 30                     | $\frac{46}{30}$            |
| pom_a4[^2]           | 12                     | 1.4*OC[^3]                     |
| SO2              | 64                     | 1                          |
| C2H6             | 30                     | 1                          |
| C3H8             | 44                     | 1                          |
| C2H4             | 28                     | 1                          |
| C3H6             | 42                     | 1                          |
| C2H2             | 26                     | 1                          |
| BIGENE           | 56                     | 1                          |
| BENZENE          | 78                     | 1                          |
| TOLUENE          | 92                     | 1                          |
| CH2O             | 30                     | 1                          |
| CH3CHO           | 44                     | 1                          |
| BIGALK           | 72                     | 1                          |
| XYLENES          | 106                    | 1                          |
| CH3OH            | 32                     | 0.15*alcohols              |
| C2H5OH           | 46                     | 0.85*alcohols              |
| CH3COCH3         | 58                     | 0.2*ketones                |
| MEK[^4]              | 72                     | 0.8*ketones                |
| HCOOH            | 46                     | 0.5*acids                  |
| CH3COOH          | 60                     | 0.5*acids                  |
| IVOC[^5]             | 184                    | 0.2*HCs[^6]                    |
| butanes          | 58                     | /                          |
| pentanes         | 72                     | /                          |
| hexanes          | 86                     | /                          |
| esters           | 184                    | /                          |
| ethers           | 81                     | /                          |
| xylene           | 106                    | /                          |
| trimethylbenzene | 120                    | /                          |
| other-aromatics  | 126                    | /                          |
| SVOC[^7]             | 310                    | 0.6*pom_a4[^6]                 |
| HCN              | 27                     | 0.003*CO                   |
| CH3CN            | 41                     | 0.002*CO                   |

- HCs include: C3H6, C3H8, C2H6, C2H4, BIGENE, BIGALK, CH3COCH3, MEK, CH3CHO, CH2O, BENZENE, TOLUENE, XYLENES[^8].

CESM also requires the numbder bc_a4, pom_a4, and SO2, which is calculated using **Equation 3**:

$$
num = \frac{{particle} \times M}{f}, \tag{3}
$$

where $num$ is the number of particles (unit: $\left(\frac{\text{particles}}{\text{cm}^2~ \text{s}}\right)\left(\frac{\text{molecules}}{\text{mole}}\right)\left(\frac{\text{g}}{\text{kg}}\right)$), particle is the total mass of the particles. $f$ is the mass per paticle, calculated by **Equation 4**:

$$
f = \rho \times \frac{\pi}{6} \times {diam}^3, \tag{4}
$$

where $\rho$ is the density, $\frac{\pi}{6}$ is a geometric factor that accounts for the volume of a sphere, $diam^3$​ is the cube of the particle's diameter. 

***Table 2** List of density ($\rho$) and diameter ($diam$).*

| Variable name                                    | $\rho$ (Unit: $g/cm^3$) | $diam$ (Unit: $cm$) |
| ------------------------------------------------ | ----------------------- | ------------------- |
| num_bc_a4                                        | 1700                    | 0.134e-6            |
| num_so4_a1 for emiss_ag_sol_was                  | 1770                    | 0.134e-6            |
| num_so4_a1 for emiss_ship                        | 1770                    | 0.261e-6            |
| num_so4_a2 for emiss_res_tran                    | 1770                    | 0.0504e-6           |
| num_so4_a1_anthro-ene-vertical for emiss_ene_ind | 1770                    | 0.261e-6            |
| num_pom                                          | 1000                    | 0.134e-6            |

Given that ESMF does not support for regridding mutiple-dimensional data, IPTpy can not generate vertial emission data yet. However, we only generate verticle anthropogenic emission data for so4_a1_anthro-ene-vertical for altitudes of 0.175, 0.225, 0.275, 0.325 $km$ based on **Equation 5**:

$$
\operatorname{so4\_a1\_anthro-ene-vertical} = \frac{0.025 \times (ene + ind)}{2e4}, \tag{5}
$$

where $ene$ and $ind$ denotes surface emission from energy and industrial sectors. 

# Notes

[^1]: Emitted black carbon (bc_a4)
[^2]: Primary organic matter (pom_a4)
[^3]: Fan, T., Liu, X., Ma, P. L., Zhang, Q., Li, Z., Jiang, Y., ... & Wang, Y. (2018). Emission or atmospheric processes? An attempt to attribute the source of large bias of aerosols in eastern China simulated by global climate models. *Atmospheric Chemistry and Physics*, 18(2), 1395-1417. [https://doi.org/10.5194/acp-18-1395-2018](https://doi.org/10.5194/acp-18-1395-2018)
[^4]: Methyl Ethyl Ketone (MEK)
[^5]: Intermediate Volatile Organic Compound (IVOC)
[^6]: Jo, D. S., Tilmes, S., Emmons, L. K., Wang, S., & Vitt, F. (2023). A new simplified parameterization of secondary organic aerosol in the Community Earth System Model Version 2 (CESM2; CAM6. 3). *Geoscientific Model Development*, 16(12), 3893–3906. [https://doi.org/10.5194/gmd-16-3893-2023](https://doi.org/10.5194/gmd-16-3893-2023)
[^7]: Semi-Volatile Organic Compound (SVOC)
[^8]: [Notes for MOZART-T1 chemistry with MAM4 aerosols in CESM2](https://wiki.ucar.edu/display/MUSICA/Grid+FINN)
