#!/bin/bash  --login
# Yuan Sun, 2025-01-31, Manchester, UK
# bash /work/n02/n02/yuansun/shell_scripts/archive/IPT-py/cams.sh
# this script is used to run FCnudged with CAMS anthropogenic emissions for testing IPT-py
# squeue -u yuansun
module load cray-python/3.9.13.1
export CESM_ROOT="/work/n02/n02/yuansun/cesm"
export CESM_VERSION="my_cesm_sandbox_cesm2.3lcz_new"
export CASE_SCRIPT="/work/n02/n02/yuansun/cesm/${CESM_VERSION}/cime/scripts"
export CASE_LOCATION=0project7
export TYPE=cams
export CASE_NAME="/work/n02/n02/yuansun/cesm/runs/${CASE_LOCATION}/ipt-py_${TYPE}"
export CASE_DOCS="CaseDocs"
export COMPSET=FCHIST
export RES=f09_f09_mg17
export PROJECT=n02-duicv
export MACH=archer2
export STARTYEAR=2018
export STARTMONTH=01
export STARTDAY=01
export ENDYEAR=2018
# the CEDS simulated starts from 2000-01-16
#export QUE=long
#export WALLTIME=96:00:00
export QUE=short
export WALLTIME=00:20:00
export ANT_PERIOD=${STARTYEAR}_${ENDYEAR}
export EMIS_DATE=20250131
export SOURCE='CAMS-GLOB-ANT'
export VERSION='v5.3'

if [ -d "${CASE_NAME}" ]; then
   rm -rf "${CASE_NAME}"
   echo "'${CASE_NAME}' exits but is deleted"
   echo "create a new case in '${CASE_NAME}'"
   cd ${CASE_SCRIPT}
   ./create_newcase --case ${CASE_NAME} --compset ${COMPSET} --res ${RES} --machine ${MACH} --queue ${QUE} --walltime ${WALLTIME} --run-unsupported
else
   echo "create a new case in '${CASE_NAME}'"
   cd ${CASE_SCRIPT}
   ./create_newcase --case ${CASE_NAME} --compset ${COMPSET} --res ${RES} --machine ${MACH} --queue ${QUE} --walltime ${WALLTIME} --run-unsupported
fi

cd ${CASE_NAME}
./xmlchange RUN_STARTDATE=${STARTYEAR}-${STARTMONTH}-${STARTDAY}
./xmlchange NTASKS_ATM=1280
./xmlchange NTASKS_CPL=1280
./xmlchange NTASKS_LND=640
./xmlchange NTASKS_ROF=640
./xmlchange NTASKS_OCN=320
./xmlchange NTASKS_ICE=320
./xmlchange ROOTPE_OCN=640
./xmlchange ROOTPE_ICE=640
./xmlchange NTASKS_WAV=1
./xmlchange NTASKS_GLC=1
./xmlchange NTASKS_ESP=1
./xmlchange NTHRDS=1
./xmlchange STOP_OPTION=ndays
./xmlchange STOP_N=1
#./xmlchange STOP_N=3
./xmlchange RESUBMIT=0
./xmlchange NTHRDS=1
./xmlchange SSTICE_DATA_FILENAME='/work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/sst/sst_HadOIBl_bc_0.9x1.25_1850_2022_c230628.nc'
./xmlchange SSTICE_YEAR_END=2021
./xmlchange SSTICE_YEAR_START=1850
./xmlchange SSTICE_YEAR_ALIGN=1850
./xmlchange RUN_TYPE=startup
./xmlchange GET_REFCASE=FALSE
./xmlchange CALENDAR=NO_LEAP
./case.setup
./preview_namelists

# vertical inputs: so4_a1 and num_a1
echo "ext_frc_specifier		= 'bc_a4 -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/emissions_ssp370/emissions-cmip6-ScenarioMIP_IAMC-AIM-ssp370-1-1_bc_a4_aircraft_vertical_mol_175001-210101_0.9x1.25_c20190222.nc',
         'NO2    -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/emissions_ssp370/emissions-cmip6-ScenarioMIP_IAMC-AIM-ssp370-1-1_NO2_aircraft_vertical_mol_175001-210101_0.9x1.25_c20190222.nc',
         'num_a1 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_num_so4_a1_anthro-ene-vertical_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'num_a1 -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/CMIP6_emissions_1750_2015/emissions-cmip6_num_a1_so4_contvolcano_vertical_850-5000_0.9x1.25_c20170724.nc',
         'num_a2 -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/CMIP6_emissions_1750_2015/emissions-cmip6_num_a2_so4_contvolcano_vertical_850-5000_0.9x1.25_c20170724.nc',
         'num_a4 -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/emissions_ssp370/emissions-cmip6-ScenarioMIP_IAMC-AIM-ssp370-1-1_num_bc_a4_aircraft_vertical_mol_175001-210101_0.9x1.25_c20190222.nc',
         'SO2    -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/emissions_ssp370/emissions-cmip6-ScenarioMIP_IAMC-AIM-ssp370-1-1_SO2_aircraft_vertical_mol_175001-210101_0.9x1.25_c20190222.nc',
         'SO2    -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/CMIP6_emissions_1750_2015/emissions-cmip6_SO2_contvolcano_vertical_850-5000_0.9x1.25_c20170724.nc',
         'SO2    -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/stratvolc/VolcanEESMv3.10_piControl_SO2_1850-2014average_ext_1deg_ZeroTrop_c181020.nc',
         'so4_a1 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_so4_a1_anthro-ene-vertical_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'so4_a1 -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/CMIP6_emissions_1750_2015/emissions-cmip6_so4_a1_contvolcano_vertical_850-5000_0.9x1.25_c20170724.nc',
         'so4_a2 -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/CMIP6_emissions_1750_2015/emissions-cmip6_so4_a2_contvolcano_vertical_850-5000_0.9x1.25_c20170724.nc'" >> user_nl_cam
# horizontal inputs
# CAM63 does not use:
#'DMS -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/emissions_${TYPE}/emissions-cmip6-SSP_DMS_other_surface_mol_175001-210101_0.9x1.25_${EMIS_DATE}.nc',
echo "srf_emis_specifier		= 'BENZENE -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_BENZENE_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'BIGALK -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_BIGALK_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'BIGENE -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_BIGENE_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'C2H2 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_C2H2_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'C2H4 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_C2H4_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'C2H4 -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/emissions_ssp370/emissions-cmip6-SSP_C2H4_other_surface_mol_175001-210101_0.9x1.25_c20190222.nc',
         'C2H5OH -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_C2H5OH_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'C2H6 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_C2H6_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'C2H6 -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/emissions_ssp370/emissions-cmip6-SSP_C2H6_other_surface_mol_175001-210101_0.9x1.25_c20190222.nc',
         'C3H6 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_C3H6_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'C3H6 -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/emissions_ssp370/emissions-cmip6-SSP_C3H6_other_surface_mol_175001-210101_0.9x1.25_c20190222.nc',
         'C3H8 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_C3H8_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'C3H8 -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/emissions_ssp370/emissions-cmip6-SSP_C3H8_other_surface_mol_175001-210101_0.9x1.25_c20190222.nc',
         'CH2O -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_CH2O_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'CH3CHO -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_CH3CHO_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'CH3CN -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_CH3CN_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'CH3COCH3 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_CH3COCH3_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'CH3COOH -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_CH3COOH_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'CH3OH -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_CH3OH_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'CO -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_CO_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'CO -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/emissions_ssp370/emissions-cmip6-SSP_CO_other_surface_mol_175001-210101_0.9x1.25_c20190222.nc',
         'E90 -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/CMIP6_emissions_1750_2015/emissions_E90global_surface_1750-2100_0.9x1.25_c20170322.nc',
         'HCN -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_HCN_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'HCOOH -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_HCOOH_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'IVOC -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_IVOC_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'MEK -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_MEK_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'NH3 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_NH3_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'NH3 -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/emissions_ssp370/emissions-cmip6-SSP_NH3_other_surface_mol_175001-210101_0.9x1.25_c20190222.nc',
         'NO -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_NO_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'NO -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/emissions_ssp370/emissions-cmip6-SSP_NO_other_surface_mol_175001-210101_0.9x1.25_c20190222.nc',
         'SVOC -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_SVOC_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'TOLUENE -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_TOLUENE_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'XYLENES -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_XYLENES_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'bc_a4 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_bc_a4_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'DMS -> /work/n02/n02/yuansun/cesm/cesm_inputdata/atm/cam/chem/emis/emissions_ssp370/emissions-cmip6-ScenarioMIP_IAMC-AIM-ssp370-1-1_DMS_bb_surface_mol_175001-210101_0.9x1.25_c20190222.nc',
         'num_a1 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_num_so4_a1_anthro-ag-ship_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'num_a2 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_num_so4_a2_anthro-res_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'num_a4 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_num_bc_a4_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'num_a4 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_num_pom_a4_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'pom_a4 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_pom_a4_anthro_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'SO2 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_SO2_anthro-ag-ship-res_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'SO2 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_SO2_anthro-ene_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'so4_a1 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_so4_a1_anthro-ag-ship_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc',
         'so4_a2 -> /work/n02/n02/yuansun/output_analysis/project7/rename/${SOURCE}${VERSION}_so4_a2_anthro-res_${ANT_PERIOD}_0.9x1.25_c${EMIS_DATE}.nc' ">> user_nl_cam 

# user_nl_cam
#echo "empty_htapes=.true." >> user_nl_cam 
echo "nhtfrq=-24" >> user_nl_cam 
echo "mfilt=1" >> user_nl_cam 

# user_nl_clm
#echo "hist_empty_htapes=.true." >> user_nl_clm
echo "flanduse_timeseries = '/work/n02/n02/yuansun/cesm/cesm_inputdata/lnd/clm2/surfdata_esmf/ctsm5.2.0/landuse.timeseries_0.9x1.25_SSP3-7.0_1850-2100_78pfts_c240216.nc'" >> user_nl_clm
echo "fsurdat = '/work/n02/n02/yuansun/cesm/cesm_inputdata/lnd/clm2/surfdata_esmf/ctsm5.2.0/surfdata_0.9x1.25_hist_2000_78pfts_c240216.nc'" >> user_nl_clm
echo "init_interp_method = 'general'" >> user_nl_clm
echo "use_init_interp = .true." >> user_nl_clm
echo "check_dynpft_consistency = .false." >> user_nl_clm
echo "hist_nhtfrq=-24" >> user_nl_clm
echo "hist_mfilt=1" >> user_nl_clm

# user_nl_mosart
echo "rtmhist_nhtfrq = -876000" >> user_nl_mosart
# user_nl_cism
echo "history_frequency = 100" >> user_nl_cism
# user_nl_cice
echo "histfreq = 'x', 'x', 'x', 'x', 'x'" >> user_nl_cice
echo "histfreq_n = 0, 0, 0, 0, 0" >> user_nl_cice
./preview_namelists
./case.build
./preview_run
#./case.submit