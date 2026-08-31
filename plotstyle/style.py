"""Style activation.

Styles are layered: SciencePlots supplies the journal base, default.mplstyle
adds only what we deliberately deviate on. No project defines rcParams of its
own - change default.mplstyle instead, so every figure everywhere follows.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import scienceplots  # noqa: F401  - importing registers the 'science' styles

STYLE_PATH = Path(__file__).parent / "default.mplstyle"

#: Journal presets from SciencePlots. It ships more; these are the ones whose
#: column widths we actually submit to.
JOURNALS = ("ieee", "nature")


def apply_style(journal: str | None = None, tex: bool = False) -> None:
    """Activate the shared plot style.

    Parameters
    ----------
    journal : str, optional
        A SciencePlots journal preset, e.g. ``"ieee"`` or ``"nature"``. Applied
        between the base style and our overrides, so column width and font size
        follow the journal while colours and grid stay ours.
    tex : bool
        Render text with a real LaTeX installation (``text.usetex``). Requires
        LaTeX; without it every plot fails. The default uses matplotlib's own
        mathtext in Computer Modern, which looks all but identical and needs no
        external dependency.

    Raises
    ------
    ValueError
        On an unknown journal name - a typo would otherwise pass silently and
        produce a figure at the wrong column width.
    """
    if journal is not None and journal not in JOURNALS:
        raise ValueError(f"Unknown journal {journal!r}; known: {', '.join(JOURNALS)}")

    styles = ["science"]
    if not tex:
        styles.append("no-latex")
    if journal is not None:
        styles.append(journal)
    styles.append(str(STYLE_PATH))

    plt.style.use(styles)

    if tex:
        plt.rcParams["text.latex.preamble"] = r"\usepackage{siunitx}\usepackage{amsmath}"
