"""Per-team goal stats per league + goal-difference distribution (6 lig, 2025/26).

Output: output/csv/team_match_stats_2526_<league>.csv (6 plików) + fig21.
"""
import _bootstrap  # noqa: F401

import pandas as pd

from ekstraklasa.config import CSV_DIR, LEAGUES
from ekstraklasa.data.loaders import load_league
from ekstraklasa.metrics.goals import goal_diff_distribution, team_goal_stats
from ekstraklasa.plots.goals_figs import fig21_goal_diff_distributions


def main() -> None:
    distributions: dict[str, pd.Series] = {}
    summary_rows = []

    for league in LEAGUES:
        matches = load_league(league)
        stats = team_goal_stats(matches)
        slug = league.replace(" ", "_")
        out = CSV_DIR / f"team_match_stats_2526_{slug}.csv"
        stats.to_csv(out, index=False)
        print(f"Wrote {out.name}  ({len(stats)} teams)")

        distributions[league] = goal_diff_distribution(matches)
        summary_rows.append({
            "League": league,
            "Total_goals_per_match": stats["Total_goals_per_match"].mean(),
            "DrawRate": stats["DrawRate"].mean(),
            "OneGoalRate": stats["OneGoalRate"].mean(),
            "BlowoutRate": stats["BlowoutRate"].mean(),
        })

    fig21_goal_diff_distributions(distributions)

    print("\n=== Per-league averages (across teams) ===")
    summary = pd.DataFrame(summary_rows).sort_values("Total_goals_per_match", ascending=False)
    with pd.option_context("display.float_format", "{:.3f}".format):
        print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
