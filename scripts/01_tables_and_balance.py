"""Tabele końcowe wszystkich sezonów Ekstraklasy + metryki balansu i predykcyjności.

Output: output/csv/tables_per_season.csv, output/csv/league_metrics.csv
"""
import _bootstrap  # noqa: F401

import numpy as np
import pandas as pd

from ekstraklasa.config import CSV_DIR, data_path
from ekstraklasa.data.loaders import load_pol_all
from ekstraklasa.data.tables import build_table
from ekstraklasa.metrics.balance import gini, hhi_normalized, noll_scully, entropy_wdl
from ekstraklasa.metrics.odds import predictability_metrics


def per_season_metrics(matches_all: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    tables = {}
    rows = []
    for season, season_matches in matches_all.groupby("Season"):
        table = build_table(season_matches)
        tables[season] = table

        n_teams = len(table)
        n_games_per_team = float(table["P"].mean())
        completed = (table["P"].max() == table["P"].min()
                     and table["P"].max() == 2 * (n_teams - 1))
        points = table["Pts"].values.astype(float)

        asd = float(np.std(points, ddof=0))
        mean_pts = float(np.mean(points))
        prediction = predictability_metrics(season_matches)

        rows.append({
            "Season": season,
            "Teams": n_teams,
            "Matches": int(season_matches.shape[0]),
            "Games_per_team": n_games_per_team,
            "Completed": completed,
            "Pts_mean": mean_pts,
            "Pts_top": float(np.max(points)),
            "Pts_bot": float(np.min(points)),
            "Pts_range": float(np.max(points) - np.min(points)),
            "ASD": asd,
            "CV": asd / mean_pts if mean_pts > 0 else float("nan"),
            "NollScully": noll_scully(points, n_games_per_team),
            "Gini": gini(points),
            "HHI_norm": hhi_normalized(points),
            "Entropy_WDL_bits": entropy_wdl(season_matches),
            "DrawRate": float((season_matches["Res"] == "D").mean()),
            "HomeWinRate": float((season_matches["Res"] == "H").mean()),
            "AwayWinRate": float((season_matches["Res"] == "A").mean()),
            "HomeAdv_goals": float((season_matches["HG"] - season_matches["AG"]).mean()),
            "AvgGoals": float((season_matches["HG"] + season_matches["AG"]).mean()),
            "Pred_n_matches": prediction["n_used"],
            "Pred_Brier": prediction["brier"],
            "Pred_LogLoss": prediction["log_loss"],
            "Pred_UpsetRate": prediction["upset_rate"],
            "Pred_FavWinRate": prediction["fav_winrate"],
        })
    metrics = pd.DataFrame(rows).sort_values("Season").reset_index(drop=True)
    return metrics, tables


def main() -> None:
    matches = load_pol_all(data_path("POL.csv"))
    print(f"Loaded {len(matches)} matches across {matches['Season'].nunique()} seasons")

    metrics, tables = per_season_metrics(matches)
    metrics_path = CSV_DIR / "league_metrics.csv"
    metrics.to_csv(metrics_path, index=False)
    print(f"\nWrote {metrics_path}")

    stacked = [t.reset_index().rename(columns={"index": "Rank"}).assign(Season=season)
               for season, t in tables.items()]
    tables_path = CSV_DIR / "tables_per_season.csv"
    pd.concat(stacked, ignore_index=True).to_csv(tables_path, index=False)
    print(f"Wrote {tables_path}")

    show_cols = ["Season", "Teams", "Matches", "Pts_mean", "ASD", "CV",
                 "NollScully", "Gini", "HHI_norm", "DrawRate", "Entropy_WDL_bits",
                 "Pred_n_matches", "Pred_Brier", "Pred_UpsetRate"]
    print("\n=== Per-season summary ===")
    with pd.option_context("display.max_columns", None, "display.width", 200,
                           "display.float_format", "{:.3f}".format):
        print(metrics[show_cols].to_string(index=False))

    print("\n=== 2025/26 vs historical (means of prior seasons) ===")
    current = metrics[metrics["Season"] == "2025/2026"].iloc[0]
    history = metrics[metrics["Season"] != "2025/2026"]
    for col in ["ASD", "CV", "NollScully", "Gini", "HHI_norm", "DrawRate",
                "Entropy_WDL_bits", "Pred_Brier", "Pred_UpsetRate"]:
        h_mean = history[col].mean()
        h_std = history[col].std()
        z = (current[col] - h_mean) / h_std if h_std > 0 else float("nan")
        print(f"  {col:<20}: 2025/26={current[col]:.3f}, "
              f"hist_mean={h_mean:.3f} (±{h_std:.3f}), z={z:+.2f}")


if __name__ == "__main__":
    main()
