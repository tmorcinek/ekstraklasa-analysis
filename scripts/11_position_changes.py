"""Średnia zmiana pozycji drużyn między 2024/25 a 2025/26 dla wszystkich 6 lig.

Beniaminkowie 2025/26 są parowani z dolnymi 3 miejscami sezonu 2024/25
(najlepszy beniaminek → najwyższa z tych pozycji).

Output: output/csv/position_changes_<league>.csv + fig20.
"""
import _bootstrap  # noqa: F401

import pandas as pd

from ekstraklasa.config import CSV_DIR, LEAGUES, data_path
from ekstraklasa.data.loaders import load_league, load_pol_season, load_topfive
from ekstraklasa.metrics.positions import position_changes
from ekstraklasa.plots.balance_figs import fig20_position_rotation


PREV_FILE = {
    "EPL": "E0-2.csv",
    "La Liga": "SP1-2.csv",
    "Bundesliga": "D1-2.csv",
    "Serie A": "I1-2.csv",
    "Ligue 1": "F1-2.csv",
}


def load_prev_season(league: str) -> pd.DataFrame:
    if league == "Ekstraklasa":
        return load_pol_season(data_path("POL.csv"), season="2024/2025")
    return load_topfive(data_path(PREV_FILE[league]))


def main() -> None:
    summary_rows = []
    all_changes: dict[str, pd.DataFrame] = {}

    for league in LEAGUES:
        prev_matches = load_prev_season(league)
        curr_matches = load_league(league)
        changes = position_changes(prev_matches, curr_matches, n_relegated=3)
        all_changes[league] = changes

        slug = league.replace(" ", "_")
        out = CSV_DIR / f"position_changes_{slug}.csv"
        changes.to_csv(out, index=False)
        print(f"Wrote {out.name}")

        summary_rows.append({
            "League": league,
            "Teams": len(changes),
            "Promoted": int((changes["Kind"] == "promoted").sum()),
            "Mean_AbsDiff": changes["AbsDiff"].mean(),
            "Max_Up": int(changes["Diff"].max()),
            "Max_Down": int(changes["Diff"].min()),
        })

    rotation = {league: float(changes["AbsDiff"].mean())
                for league, changes in all_changes.items()}
    fig20_position_rotation(rotation)

    summary = pd.DataFrame(summary_rows).sort_values("Mean_AbsDiff", ascending=False)
    print("\n=== Średnia zmiana pozycji 2024/25 → 2025/26 ===")
    with pd.option_context("display.float_format", "{:.2f}".format):
        print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
