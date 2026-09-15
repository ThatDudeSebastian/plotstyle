"""plotstyle - one consistent look for every figure, across every project.

    from plotstyle import load_data, plot_xy

    df = load_data("measurements.csv")
    plot_xy(df, x="strain", y="stress",
            xlabel=r"$\\varepsilon$ / -", ylabel=r"$\\sigma$ / MPa",
            save_as="tensile_test.pdf")

Built on SciencePlots for the journal base; default.mplstyle carries only the
deliberate deviations (Okabe-Ito palette, Computer Modern maths, two-level grid).
"""
from .io import load_data
from .plotting import apply_ticks, plot_barh, plot_scatter, plot_series, plot_xy
from .style import apply_style

__version__ = "0.1.0"

__all__ = [
    "load_data",
    "apply_style",
    "apply_ticks",
    "plot_xy",
    "plot_series",
    "plot_scatter",
    "plot_barh",
]
