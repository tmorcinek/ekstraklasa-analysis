"""Macierze punktów H2H obok siebie — Ekstraklasa vs EPL vs Liga Portugal (25/26).
Output: output/figures/leagues/fig96_h2h_three_leagues.png."""
import _bootstrap
from ekstraklasa.config import DATA_DIR
from ekstraklasa.data.loaders import load_league, load_topfive
from ekstraklasa.data.tables import build_table
from ekstraklasa.metrics.head2head import points_matrix, h2h_readings
from ekstraklasa.plots.h2h_figs import fig_h2h_side_by_side

matches = {
    "Ekstraklasa": load_league("Ekstraklasa"),
    "EPL": load_league("EPL"),
    "Liga Portugal": load_topfive(DATA_DIR / "P1.csv"),
}

matrices = {}
cyclic_rates = {}
for league, games in matches.items():
    order = build_table(games)["Team"].tolist()
    points = points_matrix(games, order)
    matrices[league] = points
    readings = h2h_readings(points)
    cyclic_rates[league] = readings["cyclic_rate"]
    print(f"{league:14s} cykle {readings['cyclic_rate']*100:.1f}% "
          f"({readings['triples_cyclic']}/{readings['triples_decisive']} rozstrzygniętych triad), "
          f"upset {readings['upset_rate_ge']*100:.1f}%")

fig_h2h_side_by_side(
    matrices,
    cyclic_rates,
    "fig96_h2h_three_leagues.png",
    title="Macierze bezpośrednich pojedynków (punkty zdobyte z każdym rywalem, 2025/26)",
)
