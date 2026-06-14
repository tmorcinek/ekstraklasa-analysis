"""Strefa strachu per drużyna — jaki udział sezonu każdy klub spędził w zasięgu strefy spadkowej.

Snapshot tabeli po każdej dacie meczowej (respektuje przełożone mecze). Ekstraklasa 2025/26:
spadają miejsca 16–18, „w zasięgu strefy" = miejsce spadkowe lub ≤6 pkt od 16. (dwie wygrane) —
ten sam próg co pasy w fig123 (54_zone_composition). Reprodukuje statystyki strefy z paper2
(siedem drużyn ≥96% sezonu, Pogoń 99%, Lech >40%).

Dane wejściowe: data/POL.csv (sezon bieżący).
Output: output/csv/teams/fear_per_team.csv
"""
import _bootstrap  # noqa: F401
import numpy as np
import pandas as pd
from ekstraklasa.config import data_path, CURRENT_SEASON, CSV_TEAMS
from ekstraklasa.data.loaders import load_pol_season
from ekstraklasa.data.tables import table_snapshots_by_date

RELEGATION_RANK = 16  # pierwsze miejsce spadkowe (spadają 16., 17., 18.)
FEAR_GAP = 6          # „w zasięgu strefy" = ≤6 pkt od 16. miejsca (dwie wygrane), jak w fig123


def in_reach_per_team(snapshots: pd.DataFrame) -> pd.DataFrame:
    border = snapshots[snapshots["Rank"] == RELEGATION_RANK].set_index("Date")["Pts"]
    enriched = snapshots.copy()
    enriched["pts_above_border"] = enriched["Pts"] - enriched["Date"].map(border)
    enriched["in_reach"] = (enriched["Rank"] >= RELEGATION_RANK) | (enriched["pts_above_border"] <= FEAR_GAP)
    rows = []
    for team, group in enriched.groupby("Team"):
        rows.append({
            "Team": team,
            "N_dates": len(group),
            "Dates_in_reach": int(group["in_reach"].sum()),
            "Pct_in_reach": round(group["in_reach"].mean(), 3),
        })
    return pd.DataFrame(rows).sort_values("Pct_in_reach", ascending=False).reset_index(drop=True)


matches = load_pol_season(data_path("POL.csv"), CURRENT_SEASON)
snapshots = table_snapshots_by_date(matches)
summary = in_reach_per_team(snapshots)

n_dates = summary["N_dates"].iloc[0]
print(f"Strefa strachu per drużyna (próg ≤{FEAR_GAP} pkt od 16.), {n_dates} dat meczowych:")
print(summary.to_string(index=False))
print(f"\nDrużyn w zasięgu przez ≥96% sezonu: {(summary['Pct_in_reach'] >= 0.96).sum()}")

CSV_TEAMS.mkdir(parents=True, exist_ok=True)
summary.to_csv(CSV_TEAMS / "fear_per_team.csv", index=False)
