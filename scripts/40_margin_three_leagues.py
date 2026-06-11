"""Rozkład |różnicy bramek| — Ekstraklasa vs EPL vs Liga Portugal (25/26), 3 panele obok siebie.
Output: output/figures/leagues/fig95_margin_eks_epl_portugal.png."""
import _bootstrap
from ekstraklasa.config import COLORS, DATA_DIR, FIG_LEAGUES
from ekstraklasa.data.loaders import load_league, load_topfive
from ekstraklasa.metrics.goals import goal_diff_distribution
from ekstraklasa.plots.goals_figs import fig_goal_diff_side_by_side

matches = {
    "Ekstraklasa": load_league("Ekstraklasa"),
    "EPL": load_league("EPL"),
    "Liga Portugal": load_topfive(DATA_DIR / "P1.csv"),
}

distributions = {league: goal_diff_distribution(games) for league, games in matches.items()}

colors = {
    "Ekstraklasa": COLORS["Ekstraklasa"],
    "EPL": COLORS["EPL"],
    "Liga Portugal": "#2e7d32",
}

fig_goal_diff_side_by_side(
    distributions,
    colors,
    "fig95_margin_eks_epl_portugal.png",
    title="Rozkład meczów wg różnicy bramkowej (2025/26)",
    output_dir=FIG_LEAGUES,
)
