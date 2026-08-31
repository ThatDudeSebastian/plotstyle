"""Typical calls.

Axis labels always as "quantity / unit" (ISO 80000), symbols as raw strings so
they are typeset as maths.
"""
from plotstyle import load_data, plot_series, plot_xy

# --- 1. A single measurement series ---------------------------------------
# Same call whether the file is measurements.csv, .xlsx or .txt
df = load_data("measurements.csv")

plot_xy(
    df,
    x="strain",
    y="stress",
    xlabel=r"$\varepsilon$ / -",
    ylabel=r"$\sigma$ / MPa",
    title="Tensile test",
    save_as="stress_strain.pdf",
)

# --- 2. Many curves, e.g. 48 thermocouples --------------------------------
# Colour from a perceptually uniform colormap plus a rotating line style.
temps = load_data("temperatures.csv")

plot_series(
    temps,
    x="time_s",
    y_cols=[c for c in temps.columns if c != "time_s"],
    xlabel=r"$t$ / s",
    ylabel=r"$T$ / °C",
    save_as="temperature_over_time.pdf",
)

# --- 3. Ansys results, read straight from the .rst ------------------------
# No export detour: ansys-dpf-core reads the solver file directly and far faster
# than writing and re-parsing a text file.
#     pip install "plotstyle[ansys]"
#
# Verified on this setup: the DPF server starts against a local Ansys 2025 R1
# install and `model.results` lists the available result types. The exact
# operator chain depends on your analysis - check `print(model.metadata)` and
# `print(model.results)` against your own .rst before trusting a snippet.
#
# import ansys.dpf.core as dpf
#
# model = dpf.Model("model.rst")
# print(model.metadata.time_freq_support)   # available time steps
# print(model.results)                      # available result types
#
# Docs: https://dpf.docs.pyansys.com/
