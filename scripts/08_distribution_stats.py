"""Statystyki rozkładu (skewness, kurtoza, NS) dla 6 lig + fig14, fig15.

Output: output/csv/distribution_stats.csv, fig14, fig15
"""
import _bootstrap  # noqa: F401

import pandas as pd

from ekstraklasa.config import CSV_DIR, LEAGUES, data_path
from ekstraklasa.data.loaders import load_topfive, load_pol_season
from ekstraklasa.data.tables import build_table
from ekstraklasa.metrics.balance import distribution_stats
from ekstraklasa.plots.normality_figs import fig14_eks_vs_bun_v2, fig15_all_leagues_grid


def main() -> None:
    tables = {}
    for name, meta in LEAGUES.items():
        if meta["is_pol"]:
            raw = load_pol_season(data_path(meta["file"]))
        else:
            raw = load_topfive(data_path(meta["file"]))
        tables[name] = build_table(raw)

    rows = []
    for name, meta in LEAGUES.items():
        points = tables[name]["Pts"].values
        stats = distribution_stats(points, meta["games"])
        stats["Liga"] = name
        rows.append(stats)

    cols_order = ["N_teams", "N_games", "Mean_pts", "Median_pts", "ASD", "ISD", "NS",
                  "Min", "Max", "Range", "Skewness", "Exc_Kurtosis"]
    stats_df = pd.DataFrame(rows).set_index("Liga")[cols_order]
    print("\n=== Statystyki rozkładu punktów 2025/26 ===")
    print(stats_df.to_string())
    out_path = CSV_DIR / "distribution_stats.csv"
    stats_df.to_csv(out_path)
    print(f"\nSaved: {out_path}")

    pts_eks = tables["Ekstraklasa"]["Pts"].values
    pts_bun = tables["Bundesliga"]["Pts"].values
    fig14_eks_vs_bun_v2(pts_eks, pts_bun)
    fig15_all_leagues_grid(tables, stats_df)


if __name__ == "__main__":
    main()
