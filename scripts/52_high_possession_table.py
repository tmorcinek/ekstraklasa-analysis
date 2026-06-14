"""Mecze z wyraźną dominacją przy piłce (posiadanie ≥ 60%) — co drużyna z nich ma.

Dla każdej ligi (2025/26): jak często drużyna z ≥60% posiadania strzela pierwszego gola,
jak często nie wychodzi na prowadzenie ani na chwilę i ile czasu średnio prowadzi.
Reprodukuje tabelę ≥60% z paper2 (26/69/12 itd.; grupa „wszystkie mecze", łącznie z 0:0).

Dane wejściowe: data/{slug}_{progress,statistics_all}.csv (snapshot 2025/26).
Output: output/csv/leagues/high_possession_table.csv
"""
import _bootstrap  # noqa: F401
import pandas as pd
from ekstraklasa.config import data_path, CSV_LEAGUES

LEAGUES = {
    "Ekstraklasa": "ekstraklasa",
    "Liga Portugal": "liga-portugal-betclic",
    "Premier League": "premier-league",
}
POSSESSION_MIN = 60


def high_possession_teams(slug: str) -> pd.DataFrame:
    progress = pd.read_csv(data_path(f"{slug}_progress.csv"))
    possession = pd.read_csv(data_path(f"{slug}_statistics_all.csv")).set_index(["match_id", "is_home"])["Ball possession"]
    home = pd.DataFrame({
        "match_id": progress["match_id"], "is_home": True,
        "scored_first": progress["first_scorer"] == "home",
        "leading_pct": progress["home_leading_pct"],
    })
    away = pd.DataFrame({
        "match_id": progress["match_id"], "is_home": False,
        "scored_first": progress["first_scorer"] == "away",
        "leading_pct": progress["away_leading_pct"],
    })
    teams = pd.concat([home, away], ignore_index=True)
    teams["possession"] = teams.set_index(["match_id", "is_home"]).index.map(possession)
    teams = teams.dropna(subset=["possession", "leading_pct"])
    return teams[teams["possession"] >= POSSESSION_MIN]


def summary(slug: str) -> dict:
    high = high_possession_teams(slug)
    return {
        "games": len(high),
        "scored_first_pct": round(100 * high["scored_first"].mean(), 1),
        "never_led_pct": round(100 * (high["leading_pct"] == 0).mean(), 1),
        "mean_leading_pct": round(high["leading_pct"].mean(), 1),
    }


table = pd.DataFrame({league: summary(slug) for league, slug in LEAGUES.items()}).T
table = table.rename_axis("league").reset_index()
CSV_LEAGUES.mkdir(parents=True, exist_ok=True)
table.to_csv(CSV_LEAGUES / "high_possession_table.csv", index=False)
print(table.to_string(index=False))
