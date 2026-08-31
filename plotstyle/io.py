"""Unified data loading layer.

Normalises CSV/Excel/TXT into one DataFrame shape so the plot functions do not
care about the source format. Only this file changes when a new tabular format
appears - style and plot logic stay untouched.

Solver result files (ANSYS .rst, LS-DYNA .d3plot, Fluent, CFX) are *not* handled
here: ansys-dpf-core reads them directly and far faster than any text export
round trip. See the README.
"""
from pathlib import Path

import pandas as pd


def load_data(path, **kwargs) -> pd.DataFrame:
    """Load measurement data from .csv, .xlsx/.xls or .txt into a DataFrame.

    Units belong in the docstring or metadata of the calling site, not in the
    column names - that keeps the plot code independent of the dataset.

    Parameters
    ----------
    path : str or Path
    **kwargs
        Passed through to the underlying pandas reader.

    Raises
    ------
    ValueError
        On an unknown extension - deliberately no silent fallback, otherwise a
        wrongly guessed separator only surfaces in the finished plot.
    """
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(path, **kwargs)
    elif suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path, **kwargs)
    elif suffix == ".txt":
        sep = kwargs.pop("sep", r"\s+")
        df = pd.read_csv(path, sep=sep, engine="python", **kwargs)
    else:
        raise ValueError(f"Unsupported format: {suffix}")

    df.columns = [str(c).strip() for c in df.columns]
    return df
