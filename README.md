EAGLE-XL Pipeline
=================

A short pipeline that uses `velociraptor` and `swiftsimio`
to produce images and plots from SWIFT runs.

The main file to check out, if you want to use this pipeline, is
the one in `run.sh`.

Getting Started
---------------

The first thing you need to do to get started with this pipeline
is to create a python virtual environment with all of the required
packages. To do this:

```
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

This you will now have all of the required packages installed. If you
already have the correct packages installed on your system, you can
probably skip this step.

You will also need to initialise and load the submodule with the
comparison data:

```
git submodule update --init --recursive
```

Then, to generate the comparison data;

```
cd velociraptor-comparison-data
git pull origin master
bash convert.sh
cd ..
```

Then you should look at `run.sh` and adapt it for your needs;
do you just want to run the pipeline on one simulation, or several?
In the latter case, you should use GNU `parallel` to parallelise
over the simulations as there are quite a few serial jobs. Set
the number of simultaneous jobs to the number of real cores
on your system.

We recommend the use of the following environment variables:
```
NUMBA_NUM_THREADS=4
OMP_NUM_THREADS=4
```
This sets the number of threads for the image making.

Generating simple output
------------------------

If all you require is halo catalogue plots (e.g. the stellar mass
function, or stellar mass-halo mass relation), all you will need
to do is run the velociraptor-python command:

```
  velociraptor-plot \
    -c auto_plotter/*.yml \
    -r registration.py \
    -p path/to/your/catalogue.properties \
    -o output/path/for/plots \
    -f png \
    -m output/path/for/plots/data.yml \
    -s mnras.mplstyle
```

Then you can use the included `useful_extras/create_comparison.py`
script if you wish to overlay several lines on a single figure.

For instance, you may have a folder of many runs called `Run1`, `Run2`,
etc. and you want to make plots for each of these. You could of course
run the whole pipeline, but that includes many plots that you may not
find useful. So, to run just the velociraptor catalogue plots, you can
do the following:

```bash
# Clone repo
git clone https://github.com/jborrow/xl-pipeline.git
cd xl-pipeline

# Grab comparison data
cd velociraptor-comparison-data
git pull origin master
bash convert.sh
cd ..

# Create plots for each
for run in {1..10}
do
  # Assuming the VR catalogue is Run{x}/stf/stf_0004.properties
  run_name="Run${run}"
  output_directory="../plots/${run_name}"
  catalogue_path="../${run_name}/stf/stf_0004.properties"
  
  mkdir -p $output_directory
  
  velociraptor-plot \
    -c auto_plotter/*.yml \
    -r registration.py \
    -p $catalogue_path \
    -o $output_directory \
    -f png \
    -m $output_directory/data.yml \
    -s mnras.mplstyle
done
```

Output
------

For each simulation, the pipeline produces:
+ A bunch of halo catalogue plots (see `auto_plotter.yml` for
  descriptions).
+ Global star formation history.
+ A summary plot of these all in one `png` with the parameters
  of the EAGLE model that are used for calibration baked in.
+ Images of the whole box (2048x2048) for visual inspection.
+ Projected gas, dark matter, and stellar surface images of
  the 100 most massive objects in the box.

