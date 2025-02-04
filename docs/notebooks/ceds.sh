#!/bin/bash
# bash '/gws/nopw/j04/duicv/yuansun/dataset/PNNL_DataHub/download_script/ceds.sh'
# This script is used to download the CEDS data from the PNNL DataHub to JASMIN using globus-cli
# Author: Yuan Sun (sunyuanzju@outlook.com)

# Define Globus endpoint IDs
export JASMIN_GLOBUS=a2f53b7f-1b4e-4dce-9b7c-349ae760fee0
export PNNL_GLOBUS=f58973c0-08c1-43a7-9a0e-71f54ddc973c

# List of VOC categories to transfer
voc_list=(VOC01-alcohols VOC02-ethane VOC03-propane VOC04-butanes VOC05-pentanes VOC06-hexanes VOC07-ethene VOC08-propene VOC09-ethyne VOC12-other VOC13-benzene VOC14-toluene VOC15-xylene VOC16-trimethylb VOC17-other VOC18-esters VOC19-ethers VOC20-chlorinate VOC21-methanal VOC22-other VOC23-ketones VOC24-acids VOC25-other)
filename_list=(VOC01-alcohols VOC02-ethane VOC03-propane VOC04-butanes VOC05-pentanes VOC06-hexanes-pl VOC07-ethene VOC08-propene VOC09-ethyne VOC12-other-alke VOC13-benzene VOC14-toluene VOC15-xylene VOC16-trimethylb VOC17-other-arom VOC18-esters VOC19-ethers VOC20-chlorinate VOC21-methanal VOC22-other-alka VOC23-ketones VOC24-acids VOC25-other-voc)
# Note that the VOC06-hexanes folder filename is VOC06-hexanes-pl

# Define the base path to the dataset
export DATA_PATH=/gws/nopw/j04/duicv/yuansun/dataset/PNNL_DataHub/CEDS_gridded_data_2021-04-21/data

# Loop over the VOC list to transfer files
for i in ${!voc_list[@]}; do
    voc=${voc_list[$i]}
    variable=${filename_list[$i]}
    dest_dir="${DATA_PATH}/VOC-speciated/${voc}/individual_files"
    filename="${variable}-em-speciated-VOC-anthro_input4MIPs_emissions_CMIP_CEDS-2021-04-21-supplemental-data_gn_200001-201912.nc"
    # Check if the directory exists, create it if not (notice the space before the closing bracket)
    if [ ! -d ${dest_dir} ]; then
        mkdir -p ${dest_dir}
    fi       

    # Define the source file path
    src_file="/CEDS/CEDS_gridded_data_2021-04-21/data/VOC-speciated/${voc}/individual_files/${filename}"

    # Perform the transfer using Globus CLI
    # globus transfer ${PNNL_GLOBUS}:${src_file} ${JASMIN_GLOBUS}:${dest_dir}
    # should be dest file rather than directory
    globus transfer ${PNNL_GLOBUS}:${src_file} ${JASMIN_GLOBUS}:${dest_dir}/${filename}
done