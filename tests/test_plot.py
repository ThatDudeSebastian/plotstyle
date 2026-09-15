"""Tests check structure, not looks. Backend 'Agg', no windows."""
import matplotlib
import pandas as pd
import pytest

matplotlib.use("Agg")

from plotstyle import apply_style, plot_barh, plot_scatter, plot_series, plot_xy  # noqa: E402


@pytest.fixture
def df():
    return pd.DataFrame({
        "t": [0, 1, 2, 3],
        "a": [0.0, 1.0, 4.0, 9.0],
        "b": [0.0, 2.0, 8.0, 18.0],
        "x": [0, 1, 0, 1],
    })


def test_style_file_is_installed():
    """Fails if package-data is missing from pyproject.toml."""
    from plotstyle.style import STYLE_PATH
    assert STYLE_PATH.is_file()


def test_apply_style_layers_our_overrides_last():
    """SciencePlots supplies the base; our palette and maths font must win."""
    apply_style()
    assert matplotlib.rcParams["mathtext.fontset"] == "cm"
    assert matplotlib.rcParams["text.usetex"] is False
    first = matplotlib.rcParams["axes.prop_cycle"].by_key()["color"][0]
    assert first.lstrip("#").lower() == "0072b2"   # Okabe-Ito, not SciencePlots'


def test_apply_style_journal_preset_changes_figure_width():
    apply_style()
    default_width = matplotlib.rcParams["figure.figsize"][0]
    apply_style(journal="ieee")
    assert matplotlib.rcParams["figure.figsize"][0] != default_width
    # our overrides still apply on top of the journal preset
    assert matplotlib.rcParams["mathtext.fontset"] == "cm"


def test_apply_style_rejects_unknown_journal():
    with pytest.raises(ValueError, match="Unknown journal"):
        apply_style(journal="natrue")


def test_plot_xy_single_series_has_no_legend(df):
    _, ax = plot_xy(df, x="t", y="a", ylabel=r"$\sigma$ / MPa")
    assert ax.get_legend() is None
    assert ax.get_ylabel() == r"$\sigma$ / MPa"


def test_plot_xy_multiple_series_has_legend(df):
    _, ax = plot_xy(df, x="t", y=["a", "b"])
    assert ax.get_legend() is not None
    assert len(ax.lines) == 2


def test_plot_series_varies_linestyle(df):
    """Secondary encoding: curves stay distinguishable in greyscale."""
    _, ax = plot_series(df, x="t", y_cols=["a", "b"])
    assert ax.lines[0].get_linestyle() != ax.lines[1].get_linestyle()


def test_plot_series_labels_override_column_names(df):
    _, ax = plot_series(df, x="t", y_cols=["a", "b"], labels={"a": "T012"})
    assert [t.get_text() for t in ax.get_legend().get_texts()] == ["T012", "b"]


def test_plot_scatter_adds_colorbar(df):
    fig, _ = plot_scatter(df, x="t", y="x", c="a", clabel=r"$T$ / °C")
    assert len(fig.axes) == 2    # main axes + colourbar


@pytest.fixture
def breakdown():
    return pd.DataFrame({
        "offer": ["A", "B"],
        "cost": [3.0, 2.0],
        "bonus": [-1.0, -4.0],
        "credit": [-1.0, -1.0],
    })


def test_plot_barh_draws_one_segment_per_row_and_column(breakdown):
    _, ax = plot_barh(breakdown, y="offer", x_cols=["cost", "bonus", "credit"])
    assert len(ax.patches) == 6
    assert [t.get_text() for t in ax.get_yticklabels()] == ["A", "B"]


def test_plot_barh_stacks_negative_segments_left_of_zero(breakdown):
    _, ax = plot_barh(breakdown, y="offer", x_cols=["cost", "bonus", "credit"])
    credit_b = ax.containers[2].patches[1]
    assert credit_b.get_x() == -4.0
    assert credit_b.get_x() + credit_b.get_width() == -5.0


def test_plot_barh_legend_uses_labels(breakdown):
    _, ax = plot_barh(breakdown, y="offer", x_cols=["cost", "bonus"], labels={"cost": "Base"})
    assert [t.get_text() for t in ax.get_legend().get_texts()] == ["Base", "bonus"]


def test_saves_file(df, tmp_path):
    out = tmp_path / "plot.pdf"
    plot_xy(df, x="t", y="a", save_as=out)
    assert out.stat().st_size > 0
