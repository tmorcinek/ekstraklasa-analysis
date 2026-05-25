"""Test kalibracji kursów bukmacherskich + Murphy decomposition.

Output: output/csv/calibration_metrics.csv
"""
import _bootstrap  # noqa: F401

import numpy as np
import pandas as pd

from ekstraklasa.config import CSV_DIR, LEAGUES, TOP5, data_path
from ekstraklasa.data.loaders import load_topfive, load_pol_season
from ekstraklasa.metrics.calibration import (
    get_probs_and_outcomes,
    murphy_decomposition,
)


def main() -> None:
    leagues = {}
    for league in TOP5:
        leagues[league] = load_topfive(data_path(LEAGUES[league]["file"]))
    leagues["Ekstraklasa"] = load_pol_season(data_path("POL.csv"))

    rows = []
    for name, matches in leagues.items():
        probs, outcomes, n_used, src = get_probs_and_outcomes(matches)
        if probs is None:
            print(f"{name}: no usable odds")
            continue
        decomp = murphy_decomposition(probs, outcomes, n_bins=10)
        rows.append({
            "League": name,
            "N_matches": n_used,
            "Odds_source": src,
            "Brier_multi": decomp["brier_multiclass"],
            "Brier_favwin": decomp["brier_favwin"],
            "Reliability": decomp["reliability"],
            "Resolution": decomp["resolution"],
            "Uncertainty": decomp["uncertainty"],
            "FavWinRate": decomp["fav_winrate"],
            "Mean_p_max": probs.max(axis=1).mean(),
        })

    metrics = pd.DataFrame(rows)
    metrics_path = CSV_DIR / "calibration_metrics.csv"
    metrics.to_csv(metrics_path, index=False)

    print("=== Calibration / Murphy decomposition ===\n")
    print("Wskaźniki dla 'wins by favourite' (binary):")
    print("  - Reliability: jak bardzo predykcja odbiega od faktycznej częstości w binie (lower=better)")
    print("  - Resolution:  jak bardzo predykcje różnicują binowe częstości (higher=better)")
    print("  - Uncertainty: nieredukowalna losowość rozkładu wyników")
    print("  Brier_favwin = Reliability − Resolution + Uncertainty\n")
    with pd.option_context("display.float_format", "{:.4f}".format, "display.width", 200):
        print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()
