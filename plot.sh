#!/bin/bash -l

# Bash function that provides plotting and analysis ability for a specific run

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
plot_run () {
  run_directory=$1
  run_name=$2
  plot_directory=$3
  snapshot_name=$4
  catalogue_name=$5

  catalogue_path=$run_directory/$catalogue_name
  output_path=$plot_directory/$run_name

  velociraptor-plot \
    -c auto_plotter/*.yml \
    -r registration.py \
    -p $catalogue_path \
    -o $output_path \
    -f png \
    -m $output_path/data.yml \
    -s mnras.mplstyle

  python3 plotting/star_formation_history.py \
    $run_name \
    $run_directory \
    $snapshot_name \
    $output_path

  python3 plotting/density_temperature.py \
    $run_name \
    $run_directory \
    $snapshot_name \
    $output_path

  python3 plotting/density_temperature_metals.py \
    $run_name \
    $run_directory \
    $snapshot_name \
    $output_path
}

# Creates a summary plot based on the above created figures, and converts
# sub-grid parameters to a text file to be plotted.
# Also converts data to Ian Vernon's specific format. Assumes that this parameter
# file is called eagle_25.yml
create_summary_plot () {
  run_directory=$1
  run_name=$2
  plot_directory=$3
  snapshot_name=$4
  catalogue_name=$5

  output_path=$plot_directory/$run_name

  old_directory=$(pwd)
  cd $output_path

  python3 ../../data_conversion/parameters.py "${run_directory}/eagle_25.yml"
  python3 ../../data_conversion/catalogue.py

  magick montage -geometry +4+4 \
    stellar_mass_function_100.png \
    stellar_mass_halo_mass_centrals_100.png \
    stellar_mass_projected_galaxy_size_100.png \
    stellar_mass_black_hole_mass_100.png \
    stellar_mass_specific_sfr_100.png \
    stellar_mass_passive_fraction_100.png \
    density_temperature_metals.png \
    star_formation_history.png \
    montage.png

  convert montage.png \
    -font Times-Roman \
    -pointsize 32 \
    -background White label:"$(cat parameters.txt)" +swap \
    -gravity Center \
    -append temp.png

  convert temp.png \
    -font Times-Roman \
    -pointsize 64 \
    -background White label:"${run_name}" +swap \
    -gravity Center \
    -bordercolor White \
    -border 0x25 \
    -append "SummaryPlot.png"

  rm temp*.png
  rm montage*.png

  cd $old_directory
}

export -f plot_run create_summary_plot
