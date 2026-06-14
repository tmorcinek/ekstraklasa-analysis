"""Pierwszy gol decyduje — liczby do rozdziału „Kto ma piłkę, ten goni".

Wśród drużyn z wyraźną przewagą przy piłce (posiadanie ≥ 60%), w meczach z bramkami:
- jak często taka drużyna jako pierwsza TRACI gola (a nie strzela),
- jak często mimo posiadania przegrywa cały mecz po stracie pierwszego gola.
Reprodukuje „74 ze 115" i straty 76/62/53% z paper2.

Dane wejściowe: data/{slug}_{progress,statistics_all}.csv (snapshot 2025/26).
Output: output/csv/leagues/first_goal_loss_rate.csv
"""
import _bootstrap  # noqa: F401
import pandas as pd
from ekstraklasa.config import data_path, CSV_LEAGUES

LEAGUES = {
    "Ekstraklasa": "ekstraklasa",
    "Premier League": "premier-league",
    "Liga Portugal": "liga-portugal-betclic",
}
POSSESSION_MIN = 60


def team_matches(slug: str) -> pd.DataFrame:
    progress = pd.read_csv(data_path(f"{slug}_progress.csv"))
    stats = pd.read_csv(data_path(f"{slug}_statistics_all.csv"))
    possession = stats.set_index(["match_id", "is_home"])["Ball possession"]
    home = pd.DataFrame({
        "match_id": progress["match_id"], "is_home": True,
        "scored_first": progress["first_scorer"] == "home",
        "conceded_first": progress["first_scorer"] == "away",
        "lost": progress["home_score"] < progress["away_score"],
    })
    away = pd.DataFrame({
        "match_id": progress["match_id"], "is_home": False,
        "scored_first": progress["first_scorer"] == "away",
        "conceded_first": progress["first_scorer"] == "home",
        "lost": progress["away_score"] < progress["home_score"],
    })
    teams = pd.concat([home, away], ignore_index=True)
    teams["possession"] = teams.set_index(["match_id", "is_home"]).index.map(possession)
    return teams.dropna(subset=["possession"])


def loss_rate_summary(slug: str) -> dict:
    teams = team_matches(slug)
    dominant = teams[teams["possession"] >= POSSESSION_MIN]
    with_goal = dominant[dominant["scored_first"] | dominant["conceded_first"]]
    conceded = with_goal[with_goal["conceded_first"]]
    return {
        "dominant_matches": len(dominant),
        "games_with_goal": len(with_goal),
        "conceded_first": len(conceded),
        "conceded_first_pct_of_dominant": round(100 * len(conceded) / len(dominant), 1),
        "lost_after_conceding": int(conceded["lost"].sum()),
        "loss_pct_after_conceding": round(100 * conceded["lost"].mean()),
    }


summary = pd.DataFrame({league: loss_rate_summary(slug) for league, slug in LEAGUES.items()}).T
summary = summary.rename_axis("league").reset_index()
CSV_LEAGUES.mkdir(parents=True, exist_ok=True)
summary.to_csv(CSV_LEAGUES / "first_goal_loss_rate.csv", index=False)
print(summary.to_string(index=False))
