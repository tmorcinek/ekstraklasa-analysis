"""Wartość pierwszego gola — jak często drużyna, która strzela pierwszego gola, wygrywa/remisuje/przegrywa.

Liczone na prawdziwym „kto strzelił pierwszy" z danych zdarzeniowych (nie z wyniku do przerwy).
Reprodukuje tabelę „pierwszy gol → wynik" z paper2 (66.1/21.9/12.0 → 88.0 itd.).

Dane wejściowe: data/{slug}_progress.csv (snapshot 2025/26).
Output: output/csv/leagues/first_goal_value.csv
"""
import _bootstrap  # noqa: F401
import pandas as pd
from ekstraklasa.config import data_path, CSV_LEAGUES

LEAGUES = {
    "Ekstraklasa": "ekstraklasa",
    "Premier League": "premier-league",
    "Liga Portugal": "liga-portugal-betclic",
}


def first_goal_outcomes(slug: str) -> dict:
    progress = pd.read_csv(data_path(f"{slug}_progress.csv"))
    scored = progress[progress["first_scorer"].isin(["home", "away"])].copy()
    scorer_goals = scored["home_score"].where(scored["first_scorer"] == "home", scored["away_score"])
    other_goals = scored["away_score"].where(scored["first_scorer"] == "home", scored["home_score"])
    won = (scorer_goals > other_goals).mean()
    drawn = (scorer_goals == other_goals).mean()
    lost = (scorer_goals < other_goals).mean()
    return {
        "games": len(scored),
        "win_pct": round(100 * won, 1),
        "draw_pct": round(100 * drawn, 1),
        "loss_pct": round(100 * lost, 1),
        "not_lost_pct": round(100 * (won + drawn), 1),
    }


summary = pd.DataFrame({league: first_goal_outcomes(slug) for league, slug in LEAGUES.items()}).T
summary = summary.rename_axis("league").reset_index()
CSV_LEAGUES.mkdir(parents=True, exist_ok=True)
summary.to_csv(CSV_LEAGUES / "first_goal_value.csv", index=False)
print(summary.to_string(index=False))
