"""Rozrzut stylu: współczynnik zmienności (CV = std/średnia) drużyn wokół średniej ligi.

Cztery cechy kształtu gry, trzy ligi (Ekstraklasa, EPL, Liga Portugal, 2025/26).
Reprodukuje tabelę rozrzutu stylu z paper2 (rozdział „W poszukiwaniu stylu").
Output: output/csv/style/style_dispersion.csv
"""
import _bootstrap  # noqa: F401
import pandas as pd
from ekstraklasa.config import DATA_DIR, CSV_STYLE
from ekstraklasa.metrics.style import add_style_metrics, team_season_means, ESA_STYLE_METRICS, STYLE_SHAPE_METRICS

LEAGUES = {
    "Ekstraklasa": "ekstraklasa_25_26_statistics.csv",
    "EPL": "premier_league_25_26_statistics.csv",
    "Liga Portugal": "liga_portugal_25_26_statistics.csv",
}


def league_team_means(filename: str) -> pd.DataFrame:
    prepared = add_style_metrics(pd.read_csv(DATA_DIR / filename))
    return team_season_means(prepared, STYLE_SHAPE_METRICS, by="team_name")


means = {league: league_team_means(filename) for league, filename in LEAGUES.items()}
cv = pd.DataFrame({league: team_means.std() / team_means.mean() for league, team_means in means.items()})
cv.index = [ESA_STYLE_METRICS[metric] for metric in cv.index]

CSV_STYLE.mkdir(parents=True, exist_ok=True)
cv.to_csv(CSV_STYLE / "style_dispersion.csv")
print("Współczynnik zmienności (%) rozrzutu stylu wokół średniej ligi:")
print((cv * 100).round(1).to_string())
