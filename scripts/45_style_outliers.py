"""Outliery stylu: ile drużyn statystycznie odstaje stylem od reszty ligi (2025/26).

Metoda: odległość każdej drużyny od centroidu jej ligi we wspólnej (pooled), znormalizowanej
przestrzeni czterech cech kształtu gry + próg Tukeya (Q3 + 1.5·IQR liczony na wszystkich ligach).
Reprodukuje wynik 0/0/2 z paper2 (w Liga Portugal odstają Sporting CP i Sporting Braga).
Output: print + output/csv/style/style_outliers.csv
"""
import _bootstrap  # noqa: F401
import numpy as np
import pandas as pd
from ekstraklasa.config import DATA_DIR, CSV_STYLE
from ekstraklasa.metrics.style import add_style_metrics, team_season_means, STYLE_SHAPE_METRICS

LEAGUES = {
    "Ekstraklasa": "ekstraklasa_25_26_statistics.csv",
    "EPL": "premier_league_25_26_statistics.csv",
    "Liga Portugal": "liga_portugal_25_26_statistics.csv",
}


def league_team_means(filename: str) -> pd.DataFrame:
    return team_season_means(add_style_metrics(pd.read_csv(DATA_DIR / filename)), STYLE_SHAPE_METRICS, by="team_name")


means = {league: league_team_means(filename) for league, filename in LEAGUES.items()}
pooled = pd.concat(means, names=["league", "team"])
pooled_z = (pooled - pooled.mean()) / pooled.std()

distances = {league: np.sqrt(((pooled_z.loc[league] - pooled_z.loc[league].mean()) ** 2).sum(axis=1))
             for league in means}
all_distances = pd.concat(distances.values())
q1, q3 = all_distances.quantile([0.25, 0.75])
threshold = q3 + 1.5 * (q3 - q1)

rows = []
print(f"Próg outliera (Tukey Q3 + 1.5·IQR) = {threshold:.2f}\n")
for league, distance in distances.items():
    outliers = distance[distance > threshold]
    names = ", ".join(f"{team} ({value:.2f})" for team, value in outliers.items()) or "—"
    print(f"  {league:14s}: {len(outliers)} outlier(s)  [{names}]")
    rows.append({"league": league, "n_outliers": len(outliers), "outliers": "; ".join(outliers.index)})

CSV_STYLE.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(CSV_STYLE / "style_outliers.csv", index=False)
