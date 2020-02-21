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

This you will now have all of the required packages installed.

You will also need to initialise and load the submodule with the
comparison data:

```
git submodule update --init --recursive
```

Then, to generate the comparison data;

```
cd velociraptor-comparison-data
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

