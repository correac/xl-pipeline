#!/bin/bash

# Example script to run analysis on a run.

# Load all sub-modules that we need
source modules.sh
source plot.sh
source image.sh

# First up, an example for running the scripts on one at a time
run_directory="Runs/Run1"
run_name="Run1"
plot_directory="Plots"
snapshot_name="eagle_0036.hdf5"
catalogue_name="stf/eagle_0036.properties.0"

plot_run $run_directory $run_name $plot_directory $snapshot_name $catalogue_name
create_summary_plot $run_directory $run_name $plot_directory $snapshot_name $catalogue_name
image_run $run_directory $run_name $plot_directory $snapshot_name $catalogue_name

# Second, baking in a run identifier so we can leverage gnu parallel.

plot_single_run () {
  run_name=$1
  run_directory="Runs/${run_name}"
  plot_directory="Plots"
  snapshot_name="eagle_0036.hdf5"
  catalogue_name="stf/eagle_0036.properties.0"

  # Check if run exists before doing any of this stuff!
  if [[ -f $run_directory/$snapshot_name ]]
  then
    plot_run $run_directory $run_name $plot_directory $snapshot_name $catalogue_name
    create_summary_plot $run_directory $run_name $plot_directory $snapshot_name $catalogue_name
    image_run $run_directory $run_name $plot_directory $snapshot_name $catalogue_name
  fi
}

ls "Runs" | grep Run | parallel -n1 -j56 "plot_single_run ${path}"
