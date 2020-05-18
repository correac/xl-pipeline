#!/bin/bash

# Example script to run analysis on a run.

# Load all sub-modules that we need
source modules.sh
source plot.sh
source image.sh

# You should have a python environment with requirements.txt installed
source /cosma7/data/dp004/dc-borr1/NewPipeline/xl-pipeline/env/bin/activate


export data_directories=(
#  "/cosma7/data/dp004/jch/EAGLE-XL/ParameterSearch-Swift/sync_from_irene/eaglexl_parameter_search_25Mpc/Runs/Wave1_Design_120ptSLHC_60plus60_25Mpc/"
#  "/cosma7/data/dp004/jch/EAGLE-XL/ParameterSearch-Swift/sync_from_irene/eaglexl_parameter_search_50Mpc_LowRes/Runs/Wave1_Design_120ptSLHC_60plus60_25Mpc"
#  "/cosma7/data/dp004/jch/EAGLE-XL/ParameterSearch-Swift/cosma/25Mpc_low_res/eaglexl_parameter_search/Runs/Wave1_Design_120ptSLHC_60plus60_25Mpc/"
#  "/cosma7/data/dp004/jch/EAGLE-XL/ParameterSearch-Swift/sync_from_irene/eaglexl_parameter_search_25Mpc_16ptLHC/Runs/Wave1_Design_16ptSLHC_50Mpc_and_25Mpc/"
#  "/cosma7/data/dp004/jch/EAGLE-XL/ParameterSearch-Swift/sync_from_irene/eaglexl_parameter_search_50Mpc_16ptLHC/Runs/Wave1_Design_16ptSLHC_50Mpc_and_25Mpc/"
#  "/cosma7/data/dp004/jch/EAGLE-XL/ParameterSearch-Swift/velociraptor_cosma/eaglexl_parameter_search_50Mpc_LowRes/output/"
#  " /cosma7/data/dp004/jch/EAGLE-XL/ParameterSearch-Swift/velociraptor_cosma/eaglexl_parameter_search_50Mpc_LowRes_AGN_fix/output/"
  "/cosma7/data/dp004/jch/EAGLE-XL/ParameterSearch-Swift/velociraptor_cosma/eaglexl_parameter_search_50Mpc_LowRes_16ptLHC/output/"
)

export plot_directories=(
#  "../Wave1_Design_120ptSLHC_60plus60_25Mpc"
#  "../Wave1_Design_120ptSLHC_60plus60_50Mpc_LowRes"
#  "../Wave1_Design_120ptSLHC_60plus60_25Mpc_LowRes"
#  "../Wave1_Design_16ptSLHC_50Mpc_and_25Mpc_25Mpc"
#  "../Wave1_Design_16ptSLHC_50Mpc_and_25Mpc_50Mpc"
#  "../Wave1_Design_120ptSLHC_60plus60_50Mpc_LowRes_ReRun"
#  "../Wave1_Design_16ptSLHC_50Mpc_and_25Mpc_50Mpc_LowRes_AGNFixed"
  "../Wave1_Design_16ptSLHC_50Mpc_and_25Mpc_50Mpc_LowRes"
)

plot_single_run () {
  run_name=$3
  plot_directory=$1
  data_directory=$2
  run_directory="${data_directory}/${run_name}"
  snapshot_name="eagle_0004.hdf5"
  catalogue_name="stf/stf_0004.properties.0"

  echo $run_name
  echo $plot_directory
  echo $run_directory

  mkdir -p $plot_directory/$run_name

  # Check if run exists before doing any of this stuff!
  if [[ -f $run_directory/$snapshot_name ]]
  then
    plot_run $run_directory $run_name $plot_directory $snapshot_name $catalogue_name
    create_summary_plot $run_directory $run_name $plot_directory $snapshot_name $catalogue_name
   #image_run $run_directory $run_name $plot_directory $snapshot_name $catalogue_name
  fi
}

export -f plot_single_run

for i in ${!data_directories[@]}; do
  data_directory=${data_directories[$i]}
  plot_directory=${plot_directories[$i]}
  baked_plot="plot_single_run ${plot_directory} ${data_directory}"

  ls $data_directory | grep Run | parallel -n1 -j40 $baked_plot 

  wait
done;
