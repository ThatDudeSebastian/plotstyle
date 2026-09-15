# plotstyle

One consistent, publication-ready look for every figure, across every project.
Written once here, pulled in as a dependency instead of copied.

```python
from plotstyle import load_data, plot_xy

df = load_data("measurements.csv")        # .csv / .xlsx / .txt, same call
plot_xy(df, x="strain", y="stress",
        xlabel=r"$\varepsilon$ / -", ylabel=r"$\sigma$ / MPa",
        save_as="tensile_test.pdf")
```

## Install

```bash
pip install "plotstyle @ git+ssh://git@github.com/ThatDudeSebastian/plotstyle.git"
```

You do **not** clone this repo to use it — `pip` fetches it. Clone only to develop
*on* plotstyle: `git clone …` then `pip install -e ".[dev]"`.

> ⚠️ **Never `pip install plotstyle` bare.** An unrelated package of the same name
> exists on PyPI (v1.2.4, "Matplotlib/seaborn style presets matching scientific journal
> requirements"). It would install cleanly and then fail on
> `from plotstyle import plot_xy`. Always use the full `git+ssh://` URL, and never
> `pip install --upgrade plotstyle` — that resolves to PyPI and silently replaces this
> package.

### Pinning for reproducibility

The line above tracks `main`, so projects pick up improvements. That is right while work
is ongoing and wrong the moment a figure goes into a publication: reinstalling a year
later would give different code. When a project reaches a milestone, pin the tag and
record the environment:

```toml
dependencies = ["plotstyle @ git+ssh://git@github.com/ThatDudeSebastian/plotstyle.git@v0.1.0"]
```

```bash
pip freeze > requirements-lock.txt   # commit this alongside the results
```

Tags are immutable once pushed. `git tag -l` lists them.

## What is in it

| Function | Use |
|---|---|
| `apply_style(journal=None, tex=False)` | Activate the style; `journal="ieee"` / `"nature"` for submission widths |
| `plot_xy(df, x, y, …)` | One or a few curves. Up to ~8 series. |
| `plot_series(df, x, y_cols, …)` | Many curves — colormap **plus** rotating line style |
| `plot_scatter(df, x, y, c=…, …)` | Scatter, optionally coloured by a third column with a colourbar |
| `plot_barh(df, y, x_cols, …)` | Horizontal stacked bars; negative segments stack left of zero (costs vs. credits) |
| `apply_ticks(ax, …)` | Two-level tick and grid subdivision |
| `load_data(path)` | CSV/Excel/TXT into one DataFrame shape |

## How the style is built

[SciencePlots](https://github.com/garrettj403/SciencePlots) supplies the journal
base (`science` + `no-latex`); `default.mplstyle` layers on only the deliberate
deviations. Upstream improvements carry over; our decisions win.

> **Known risk.** SciencePlots 2.2.2 calls `read_style_directory` and
> `update_nested_dict`, deprecated in matplotlib 3.11 and slated for removal in
> 3.13. If upstream does not fix it in time, importing it will break. The exit is
> cheap: drop `scienceplots` from `style.py` and `pyproject.toml`, and move the
> handful of base settings (figure size 3.5×2.625 in, serif font, thin spines)
> into `default.mplstyle`. Only the `ieee`/`nature` presets would be lost.

- **Maths without LaTeX.** `mathtext.fontset: cm` gives Computer Modern, so
  `r"$\sigma$ / MPa"` is typeset like LaTeX with no LaTeX installed. With a real
  distribution available, `apply_style(tex=True)`.
- **Axis labels** follow ISO 80000: `quantity / unit`, not `quantity [unit]`.
- **Colour.** Okabe-Ito (colourblind-safe, Okabe & Ito 2008) in fixed order for
  categorical series; `viridis` for continuous quantities. Not `rainbow`/`jet` —
  they create contrast steps that do not exist in the data.
- **Beyond ~8 curves** use `plot_series()`: it encodes with line style as well,
  so the figure survives greyscale printing and colour vision deficiency.
- **No rcParams in projects.** Style changes belong in `default.mplstyle`, so
  every figure in every project follows.

## Reading solver results

Do **not** export to text and parse it back. `ansys-dpf-core` reads Ansys result
files directly — the same engine Mechanical uses, from ordinary Python:

```bash
pip install "plotstyle[ansys]"
```

```python
import ansys.dpf.core as dpf

model = dpf.Model("model.rst")
print(model.metadata.time_freq_support)   # time steps
print(model.results)                      # available result types
```

Supported: MAPDL (`.rst`, `.rth`, `.mode`, `.rfrq`, `.rdsp`), LS-DYNA
(`.d3plot`, `.binout`), Fluent and CFX. Requires a local Ansys installation
(2023 R1 or newer) — the DPF server starts by itself. Verified here against
Ansys 2025 R1. Docs: <https://dpf.docs.pyansys.com/>

`load_data()` stays for plain tabular files; it is a thin wrapper around pandas.
