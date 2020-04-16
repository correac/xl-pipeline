"""
A script for plotting multiple data lines on one set of observational data.
This uses the `data.yml` files from the pipeline.

See the help (from argparse) for more information. That can be seen by using

python3 create_comparison.py -h
"""

import matplotlib.pyplot as plt
import yaml
import unyt

from typing import Union, List, Dict
from velociraptor.autoplotter.objects import VelociraptorPlot, valid_line_types
from velociraptor.autoplotter.plot import decorate_axes


class FakeCatalogue(object):
    """
    Fake VelociraptorCatalogue used to store redshift and
    scale factor information if available.
    """

    def __init__(self, z=0.0, a=0.0):
        self.z = float(z)
        self.a = float(a)
        return


def load_yaml_line_data(
    paths: Union[str, List[str]], names: Union[str, List[str]]
) -> Dict[str, Dict]:
    """
    Load the ``yaml`` data from the files for lines.

    Parameters
    ----------

    paths: Union[str, List[str]]
        Paths to yaml data files to load.
    
    names: Union[str, List[str]]
        Names of the simulations that correspond to the yaml data files.
        Will be placed in the legends of the plots.
        

    Returns
    -------
    
    data: Dict[str, Dict]
        Dictionary of line data read directly from the files.
    """

    if not isinstance(paths, list):
        paths = [paths]
        names = [names]

    data = {}

    for path, name in zip(paths, names):
        with open(path, "r") as handle:
            data[name] = yaml.load(handle, Loader=yaml.Loader)

    return data


def recreate_single_figure(
    plot: VelociraptorPlot,
    line_data: Dict[str, Dict],
    output_directory: str,
    file_type: str,
) -> None:
    """
    Recreates a single figure using the data in ``line_data`` and the metadata in
    ``plot``.
    
    Parameters
    ----------

    plot: VelociraptorPlot
        Velociraptor plot instance (from AutoPlotter).

    line_data: Dict[str, Dict]
        Global line data, obtained from the ``load_yaml_line_data`` function.

    output_directory: str
        Output directory for the plot

    file_type: str
        Output file type (e.g. ``png``)
    """

    try:
        first_line_metadata = line_data[list(line_data.keys())[0]]["metadata"]
        fake_catalogue = FakeCatalogue(
            z=first_line_metadata["redshift"], a=first_line_metadata["scale_factor"]
        )
    except KeyError:
        fake_catalogue = FakeCatalogue()

    fig, ax = plt.subplots()

    # Add simulation data
    for line_type in valid_line_types:
        line = getattr(plot, f"{line_type}_line", None)
        if line is not None:
            for name, data in line_data.items():
                ax.set_xlabel(data[plot.filename].get("x_label"))
                ax.set_ylabel(data[plot.filename].get("y_label"))

                this_line_dict = data[plot.filename]["lines"][line_type]
                centers = unyt.unyt_array(this_line_dict["centers"], units=plot.x_units)
                heights = unyt.unyt_array(this_line_dict["values"], units=plot.y_units)
                errors = unyt.unyt_array(this_line_dict["scatter"], units=plot.y_units)

                if line.scatter == "none":
                    ax.plot(centers, heights, label=name)
                elif line.scatter == "errorbar":
                    ax.errorbar(centers, heights, yerr=errors, label=name)
                elif line.scatter == "shaded":
                    (mpl_line,) = ax.plot(centers, heights, label=name)

                    # Deal with different + and -ve errors
                    if errors.shape[0]:
                        if errors.ndim > 1:
                            down, up = errors
                        else:
                            up = errors
                            down = errors
                    else:
                        up = 0
                        down = 0

                    ax.fill_between(
                        centers,
                        heights - down,
                        heights + up,
                        color=mpl_line.get_color(),
                        alpha=0.3,
                        linewidth=0.0,
                    )

    # Add observational data second to allow for colour precedence
    # to go to runs
    for data in plot.observational_data:
        data.plot_on_axes(ax, errorbar_kwargs=dict(zorder=-10))

    # Finally set up metadata
    if plot.x_log:
        ax.set_xscale("log")
    if plot.y_log:
        ax.set_yscale("log")

    ax.set_xlim(*unyt.unyt_array(plot.x_lim, units=plot.x_units))
    ax.set_ylim(*unyt.unyt_array(plot.y_lim, units=plot.y_units))

    decorate_axes(
        ax,
        catalogue=fake_catalogue,
        comment=plot.comment,
        legend_loc=plot.legend_loc,
        redshift_loc=plot.redshift_loc,
        comment_loc=plot.comment_loc,
    )

    fig.savefig(f"{output_directory}/{plot.filename}.{file_type}")
    plt.close(fig)


if __name__ == "__main__":
    import argparse as ap
    from velociraptor.autoplotter.objects import AutoPlotter
    from velociraptor.autoplotter.metadata import AutoPlotterMetadata
    from matplotlib import __version__
    from matplotlib.pyplot import style

    parser = ap.ArgumentParser(
        description=(
            "Takes in several data.yml files (you can use standard globbing "
            "to select these) and produces figures that contain all the relevant "
            "lines for these, as well as observational data from the original "
            "configuration files."
        ),
        epilog=(
            "Example usage:\n"
            "  python3 create_comparison.py -c configs/*.yml -o comparison_plots -f png -i "
            "Run{20,30,40}/data.yml -t Run20 Run30 Run40"
        ),
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help=(
            "Configuration .yml file. Required. Can also be supply a list "
            "of parameters, like x.yml y.yml z.yml, all separated by spaces."
        ),
        nargs="*",
    )

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Location of the data yaml files containing line information. Required.",
        nargs="*",
    )

    parser.add_argument(
        "-t",
        "--titles",
        required=True,
        default=None,
        help="Names for each of the lines on the plot. Required.",
        nargs="*",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        default=".",
        help='Output directory for figures. Default: "./".',
    )

    parser.add_argument(
        "-f",
        "--file-type",
        type=str,
        required=False,
        default="pdf",
        help="Output file type of the figures. Default: pdf.",
    )

    parser.add_argument(
        "-d",
        "--debug",
        required=False,
        default=False,
        action="store_true",
        help="Run in debug mode if this flag is present. Default: no.",
    )

    parser.add_argument(
        "-s",
        "--stylesheet",
        required=False,
        default=None,
        help="Path to the matplotlib stylesheet to apply for the plots. Default: None.",
    )

    args = parser.parse_args()

    if args.debug:
        from tqdm import tqdm

    def print_if_debug(string: str) -> None:
        if args.debug:
            print(string)

    print_if_debug("Running in debug mode. Arguments given are:")
    for name, value in dict(vars(args)).items():
        print_if_debug(f"{name}: {value}")

    if args.stylesheet is not None:
        print_if_debug(f"Matplotlib version: {__version__}.")
        print_if_debug(f"Applying matplotlib stylesheet at {args.stylesheet}.")
        style.use(args.stylesheet)

    print_if_debug(f"Generating initial AutoPlotter instance for {args.config}.")
    auto_plotter = AutoPlotter(args.config)

    print_if_debug("Converting AutoPlotter.plots to a tqdm instance.")
    if args.debug:
        auto_plotter.plots = tqdm(auto_plotter.plots, desc="Creating figures")

    print_if_debug(f"Loading line data from yaml files: {args.input}")
    line_data = load_yaml_line_data(paths=args.input, names=args.titles)

    for plot in auto_plotter.plots:
        try:
            recreate_single_figure(
                plot=plot,
                line_data=line_data,
                output_directory=args.output,
                file_type=args.file_type,
            )
        except:
            print_if_debug(f"Failed to create plot for {plot.filename}.")
