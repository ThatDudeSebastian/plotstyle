"""Shared plotting functions.

The style is set centrally in default.mplstyle - no rcParams here, only plot
logic. New plot types go into this file as further functions, not as copies in
individual project scripts.

Axis labels follow ISO 80000: "quantity / unit", not "quantity [unit]". Write
symbols as raw strings and they are typeset as maths:

    xlabel=r"$t$ / s", ylabel=r"$T$ / °C", ylabel=r"$\\sigma$ / MPa"
"""
from itertools import cycle

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from .style import apply_style

# Secondary encoding for many series: curves stay distinguishable without
# colour - in greyscale print and with colour vision deficiency.
LINESTYLES = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 2))]


def _new_ax(ax):
    return (ax.figure, ax) if ax is not None else plt.subplots()


def _finish(fig, ax, xlabel, ylabel, title, save_as):
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    if save_as:
        fig.savefig(save_as)
    return fig, ax


def apply_ticks(ax, x_major=None, x_minor=2, y_major=None, y_minor=2):
    """Set the two-level tick and grid subdivision.

    Without arguments the minor subdivision is derived from the major ticks.
    For fixed scales - temperature in steps of 100 with minor steps of 25, say -
    pass ``y_major=100, y_minor=25``: a minor value below the major step is read
    as a step width, otherwise as a number of subdivisions.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
    x_major, y_major : float, optional
        Fixed step width of the major ticks. None lets matplotlib choose.
    x_minor, y_minor : float
        Minor step width, or number of subdivisions per major interval.
    """
    for axis, major, minor in ((ax.xaxis, x_major, x_minor), (ax.yaxis, y_major, y_minor)):
        if major is not None:
            axis.set_major_locator(mticker.MultipleLocator(major))
        if minor is None:
            continue
        if major is not None and minor < major:
            axis.set_minor_locator(mticker.MultipleLocator(minor))
        else:
            axis.set_minor_locator(mticker.AutoMinorLocator(int(minor)))

    ax.grid(True, which="major", alpha=0.3)
    ax.grid(True, which="minor", alpha=0.15, linewidth=0.3)
    return ax


def plot_xy(df, x, y, ax=None, xlabel=None, ylabel=None, title=None,
            save_as=None, **plot_kwargs):
    """Plot one or more y columns against x in the shared style.

    ``y`` is a single column name or a sequence of them. Beyond about 8 curves
    use plot_series() instead - the palette here has 8 fixed positions and would
    start repeating.
    """
    apply_style()
    fig, ax = _new_ax(ax)

    y_cols = [y] if isinstance(y, str) else list(y)
    for col in y_cols:
        ax.plot(df[x], df[col], label=str(col), **plot_kwargs)

    if len(y_cols) > 1:
        ax.legend()
    apply_ticks(ax)
    return _finish(fig, ax, xlabel or x,
                   ylabel or (y_cols[0] if len(y_cols) == 1 else None),
                   title, save_as)


def plot_series(df, x, y_cols, ax=None, cmap="viridis", labels=None,
                xlabel=None, ylabel=None, title=None, legend_ncol=2,
                save_as=None, **plot_kwargs):
    """Many curves against a shared x axis - 48 thermocouples, for instance.

    Colour comes from a perceptually uniform colormap and the line style rotates
    on top of it, so the curves remain distinguishable in greyscale and with
    colour vision deficiency.

    Parameters
    ----------
    y_cols : sequence of str
        Columns to plot, in the order they should be coloured.
    cmap : str
        Perceptually uniform colormap. 'rainbow'/'jet' are deliberately not the
        default: they create contrast steps that do not exist in the data.
    labels : dict, optional
        Mapping column name -> legend text. Columns without an entry keep their
        own name.
    """
    apply_style()
    fig, ax = _new_ax(ax)

    y_cols = list(y_cols)
    colors = plt.get_cmap(cmap)(
        [i / max(len(y_cols) - 1, 1) for i in range(len(y_cols))]
    )
    styles = cycle(LINESTYLES)
    labels = labels or {}

    # strict=False on purpose: styles is an infinite cycle, y_cols sets the length.
    for col, color, style in zip(y_cols, colors, styles, strict=False):
        ax.plot(df[x], df[col], color=color, linestyle=style,
                label=str(labels.get(col, col)), **plot_kwargs)

    ax.legend(ncol=legend_ncol)
    apply_ticks(ax)
    return _finish(fig, ax, xlabel or x, ylabel, title, save_as)


def plot_scatter(df, x, y, c=None, ax=None, cmap="viridis", clabel=None,
                 xlabel=None, ylabel=None, title=None, save_as=None,
                 **scatter_kwargs):
    """Scatter plot, optionally coloured by a third column with a colourbar.

    Typical case: sensor positions in a plane, coloured by the value measured
    there.

    Parameters
    ----------
    c : str, optional
        Column driving the colour. None draws all points in one colour.
    clabel : str, optional
        Colourbar label, again as "quantity / unit".
    """
    apply_style()
    fig, ax = _new_ax(ax)
    scatter_kwargs.setdefault("edgecolor", "black")
    scatter_kwargs.setdefault("linewidth", 0.3)

    if c is None:
        ax.scatter(df[x], df[y], **scatter_kwargs)
    else:
        sc = ax.scatter(df[x], df[y], c=df[c], cmap=cmap, **scatter_kwargs)
        fig.colorbar(sc, ax=ax).set_label(clabel or c)

    ax.set_aspect("equal", adjustable="datalim")
    apply_ticks(ax)
    return _finish(fig, ax, xlabel or x, ylabel or y, title, save_as)


def plot_barh(df, y, x_cols, ax=None, colors=None, labels=None, xlabel=None,
              title=None, save_as=None):
    """Horizontal stacked bars: one bar per row, one segment per column.

    Positive segments stack rightwards from zero, negative ones leftwards, so a
    single bar shows costs and credits at once - a cost breakdown, for instance.
    The first row is drawn at the top.

    Parameters
    ----------
    y : str
        Column holding the bar labels.
    x_cols : sequence of str
        Segment columns, stacked outwards from zero in this order.
    colors : sequence, optional
        One colour per column. None follows the style's colour cycle.
    labels : dict, optional
        Mapping column name -> legend text. Columns without an entry keep their
        own name.
    """
    apply_style()
    fig, ax = _new_ax(ax)

    x_cols = list(x_cols)
    labels = labels or {}
    positions = np.arange(len(df))
    right = np.zeros(len(df))
    left = np.zeros(len(df))

    for col, color in zip(x_cols, colors or [None] * len(x_cols), strict=True):
        values = df[col].to_numpy(dtype=float)
        # Zero-width segments start at 0: at the stack's outer end their sticky edge
        # would pin the axis limit there and swallow the margin.
        start = np.select([values > 0, values < 0], [right, left], 0.0)
        # Surface-coloured edges leave a gap between neighbouring segments.
        ax.barh(positions, values, left=start, color=color,
                edgecolor=ax.get_facecolor(), linewidth=0.8, label=str(labels.get(col, col)))
        right += np.clip(values, 0, None)
        left += np.clip(values, None, 0)

    ax.axvline(0, color="black", linewidth=0.6)
    ax.set_yticks(positions, df[y])
    ax.invert_yaxis()
    ax.legend()
    apply_ticks(ax, y_minor=None)
    # Categories have no minor subdivision, and grid lines between bars are noise.
    ax.yaxis.set_minor_locator(mticker.NullLocator())
    ax.grid(False, axis="y", which="both")
    return _finish(fig, ax, xlabel, None, title, save_as)
