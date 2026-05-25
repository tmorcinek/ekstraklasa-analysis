"""Cross-league: te same metryki co 01_, ale dla 6 lig w sezonie 2025/26 + historia Ekstraklasy.

Output: output/csv/all_league_metrics.csv, output/csv/tables_2526_all_leagues.csv
"""
import _bootstrap  # noqa: F401

import numpy as np
import pandas as pd

from ekstraklasa.config import CSV_DIR, CURRENT_SEASON, LEAGUES, TOP5, data_path
from ekstraklasa.data.loaders import load_topfive, load_pol_all
from ekstraklasa.data.tables import build_table
from ekstraklasa.metrics.balance import gini, hhi_normalized, noll_scully, entropy_wdl
from ekstraklasa.metrics.odds import predictability_metrics


def metrics_for(matches: pd.DataFrame, league: str, season: str) -> dict:
    table = build_table(matches)
    n_teams = len(table)
    n_games_per_team = float(table["P"].mean())
    points = table["Pts"].values.astype(float)
    mean_pts = float(np.mean(points))
    prediction = predictability_metrics(matches)
    asd = float(np.std(points, ddof=0))
    goal_diffs = (matches["HG"] - matches["AG"]).abs()
    return {
        "League": league,
        "Season": season,
        "Teams": n_teams,
        "Matches": int(matches.shape[0]),
        "Games_per_team_mean": n_games_per_team,
        "Pts_mean": mean_pts,
        "Pts_top": float(np.max(points)),
        "Pts_bot": float(np.min(points)),
        "Pts_range": float(np.max(points) - np.min(points)),
        "ASD": asd,
        "CV": asd / mean_pts if mean_pts > 0 else float("nan"),
        "NollScully": noll_scully(points, n_games_per_team),
        "Gini": gini(points),
        "HHI_norm": hhi_normalized(points),
        "Entropy_WDL_bits": entropy_wdl(matches),
        "DrawRate": float((matches["Res"] == "D").mean()),
        "HomeWinRate": float((matches["Res"] == "H").mean()),
        "AwayWinRate": float((matches["Res"] == "A").mean()),
        "HomeAdv_goals": float((matches["HG"] - matches["AG"]).mean()),
        "AvgGoals": float((matches["HG"] + matches["AG"]).mean()),
        "BlowoutRate": float((goal_diffs >= 2).mean()),
        "OneGoalRate": float((goal_diffs == 1).mean()),
        "Pred_src": prediction["src"],
        "Pred_n_matches": prediction["n_used"],
        "Pred_Brier": prediction["brier"],
        "Pred_LogLoss": prediction["log_loss"],
        "Pred_UpsetRate": prediction["upset_rate"],
    }


def main() -> None:
    rows = []
    tables_current = {}

    for league in TOP5:
        matches = load_topfive(data_path(LEAGUES[league]["file"]))
        rows.append(metrics_for(matches, league, CURRENT_SEASON))
        tables_current[league] = build_table(matches)

    pol_all = load_pol_all(data_path("POL.csv"))
    for season, season_matches in pol_all.groupby("Season"):
        rows.append(metrics_for(season_matches, "Ekstraklasa", season))
        if season == CURRENT_SEASON:
            tables_current["Ekstraklasa"] = build_table(season_matches)

    metrics = pd.DataFrame(rows)
    metrics_path = CSV_DIR / "all_league_metrics.csv"
    metrics.to_csv(metrics_path, index=False)
    print(f"Wrote {metrics_path}  ({len(metrics)} rows)")

    current = metrics[metrics["Season"] == CURRENT_SEASON].copy()
    current = current.sort_values("NollScully").reset_index(drop=True)
    show = ["League", "Teams", "Matches", "Games_per_team_mean",
            "ASD", "CV", "NollScully", "Gini", "HHI_norm",
            "Entropy_WDL_bits", "DrawRate", "HomeAdv_goals", "AvgGoals",
            "Pred_n_matches", "Pred_Brier", "Pred_UpsetRate", "Pred_src"]
    print("\n=== 2025/26 — porównanie 6 lig (sortowane po Noll-Scully) ===")
    with pd.option_context("display.max_columns", None, "display.width", 220,
                           "display.float_format", "{:.3f}".format):
        print(current[show].to_string(index=False))

    print("\n=== Ekstraklasa 2025/26 vs Top 5 (means) ===")
    eks = current[current["League"] == "Ekstraklasa"].iloc[0]
    top5 = current[current["League"] != "Ekstraklasa"]
    for col in ["ASD", "CV", "NollScully", "Gini", "HHI_norm",
                "Entropy_WDL_bits", "Pred_Brier", "Pred_UpsetRate"]:
        t_mean = top5[col].mean()
        t_std = top5[col].std()
        z = (eks[col] - t_mean) / t_std if t_std > 0 else float("nan")
        print(f"  {col:<20}: Eks={eks[col]:.3f}, Top5_mean={t_mean:.3f} (±{t_std:.3f}), z={z:+.2f}")

    stacked = [t.reset_index().rename(columns={"index": "Rank"}).assign(League=league)
               for league, t in tables_current.items()]
    tables_path = CSV_DIR / "tables_2526_all_leagues.csv"
    pd.concat(stacked, ignore_index=True).to_csv(tables_path, index=False)
    print(f"\nWrote {tables_path}")


if __name__ == "__main__":
    main()
