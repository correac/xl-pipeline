#!/bin/bash

# Example script to run analysis on a run.

# Load all sub-modules that we need
source modules.sh
source plot.sh
source image.sh

# You should have a python environment with requirements.txt installed
source env/bin/activate

# This script expects that you have one top-level directory,
# $run_directory, containing multiple runs called $run_names.
# It loops over them, and the snapshot numbers $snap_numbers,
# assuming that you have snapshots named eagle_$snap_numbers, 
# and halo catalogues named halo_$snap_numbers.properties.
# It makes plots in $run_driectory/plots/snapshot_$snapnum/...

export run_directory=/path/to/runs

# Names of your runs that you wish to loop over (could just be one!)
export run_names=(
  MyFavouriteRun
)

# Snapshot numbers
export snap_numbers=(
  "0000"
  "0001"
  "0002"
)

plot_single_run () {
  snapnum=$4
  run_name=$3
  plot_directory=$1
  data_directory=$2
  run_directory="${data_directory}/${run_name}"
  snapshot_name="eagle_${snapnum}.hdf5"
  catalogue_name="halo_${snapnum}.properties"

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

for run_name in ${run_names[@]}; do
  for snapnum in ${snap_numbers[@]}; do
    plot_directory=$run_directory/plots/snapshot_$snapnum
    plot_single_run $plot_directory $run_directory $run_name $snapnum &
 done;
 wait;
done;
