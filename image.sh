#!/bin/bash -l

# Bash function that provides image creation analaysis for a specific run.

# Parameters are as follows:
# 1. Run directory - location of the run. E.g. Run/Run1
# 2. Run name - symbolic name for this run. E.g. MyRun
# 3. Plot directory - where the plots should be stored. E.g. Plots
# 4. Snapshot name - name of the snapshot. E.g. eagle_0036.hdf5
# 5. Catalogue name - name of the halo properties. E.g. stf/stf.properties
#
# For the above, this will assume that:
# + There is a directory Run/Run1
# + The snapshot lives at Run/Run1/eagle_0036.hdf5
# + The halo catalogue lives at Run/Run1/stf/stf.properties
# + You want the plots to be saved in Plots/MyRun
# + You want the run to be called MyRun on the summary plot.
#
image_run () {
  run_directory=$1
  run_name=$2
  plot_directory=$3
  snapshot_name=$4
  catalogue_name=$5

  catalogue_path=$run_directory/$catalogue_name
  output_path=$plot_directory/$run_name
  snapshot_path=$run_directory/$snapshot_name

  python3 images/imaging.py $snapshot_path $catalogue_path $output_path
  python3 images/halo_images.py $snapshot_path $catalogue_path $output_path
}

export -f image_run
