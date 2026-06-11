"""Dwa kandydaty na wykres otwierający rozdział o stylu (Ekstraklasa 25/26):
- fig89: boxplot posiadania per drużyna (rozrzut mecz-po-meczu), sortowany wg średniej.
- fig90: wariant fig60 — 4 cechy kształtu gry, 1 rząd × 4 kolumny, słupki wg tabeli.
Output: figures/style/.
"""
import _bootstrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ekstraklasa.config import data_path, FIG_STYLE, TEAM_MAP, COLORS, CURRENT_SEASON
from ekstraklasa.metrics.style import (
    add_style_metrics, team_season_means, ESA_STYLE_METRICS, STYLE_SHAPE_METRICS)
from ekstraklasa.data.loaders import load_pol_season
from ekstraklasa.data.tables import build_league_table
from ekstraklasa.plots.style import save_figure, clean_axes

prepared = add_style_metrics(pd.read_csv(data_path("ekstraklasa_25_26_statistics.csv")))
prepared["team_short"] = prepared["team_name"].map(TEAM_MAP)

matches = load_pol_season(data_path("POL.csv"), CURRENT_SEASON)
table = build_league_table("Ekstraklasa", matches).reset_index(drop=True)
final_rank = pd.Series(
    {TEAM_MAP.get(team, team): rank + 1 for rank, team in enumerate(table["Team"])},
    name="final_rank",
).rename_axis("team_short")

# ── fig89: boxplot posiadania per drużyna, sortowany wg średniej ───────────────
by_team = prepared.groupby("team_short")["Ball possession"]
order = by_team.mean().sort_values().index.tolist()
league_mean = prepared["Ball possession"].mean()

fig, ax = plt.subplots(figsize=(13, 6))
boxes = ax.boxplot([by_team.get_group(team).values for team in order], tick_labels=order,
                   patch_artist=True, medianprops=dict(color="#222", linewidth=1.5),
                   flierprops=dict(marker="o", markersize=3, alpha=0.5))
for patch in boxes["boxes"]:
    patch.set_facecolor(COLORS["Ekstraklasa"])
    patch.set_alpha(0.45)
ax.axhline(league_mean, color="#b00", linestyle="--", linewidth=1.3,
           label=f"średnia ligi = {league_mean:.1f}%")
ax.set_xticklabels(order, rotation=45, ha="right", fontsize=9)
ax.set_ylabel("Posiadanie piłki w meczu (%)", fontsize=11)
ax.set_title("Posiadanie piłki w Ekstraklasie — rozrzut każdej drużyny w sezonie (2025/26)\n"
             "(drużyny wg rosnącej średniej; mediany skupione wokół połowy, brak wyróżnika)",
             fontsize=13, weight="bold")
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
clean_axes(ax)
fig.tight_layout()
save_figure(fig, "fig89_possession_boxplot_eks.png", output_dir=FIG_STYLE)

# ── fig90: wariant fig60 — 4 cechy kształtu, 1 rząd × 4 kolumny ────────────────
table_order = final_rank.sort_values().index.tolist()
means = team_season_means(prepared, STYLE_SHAPE_METRICS, by="team_short").reindex(table_order)
rank_colors = plt.cm.RdYlGn(np.linspace(0.9, 0.1, len(table_order)))
short_names = [team.split()[0][:8] for team in table_order]

fig, axes = plt.subplots(1, len(STYLE_SHAPE_METRICS), figsize=(18, 5), facecolor="#f8f8f8")
for ax, metric in zip(axes, STYLE_SHAPE_METRICS):
    ax.set_facecolor("#f8f8f8")
    values = means[metric].values
    median = np.median(values)
    ax.bar(range(len(table_order)), values, color=rank_colors, alpha=0.85, width=0.7)
    ax.axhline(median, color="#555", linestyle="--", linewidth=1, alpha=0.7,
               label=f"mediana={median:.1f}")
    ax.set_xticks(range(len(table_order)))
    ax.set_xticklabels(short_names, rotation=45, ha="right", fontsize=7.5)
    ax.set_title(ESA_STYLE_METRICS[metric], fontsize=10, weight="bold")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
fig.suptitle("Cechy kształtu gry drużyn Ekstraklasy 2025/26 — średnie sezonowe\n"
             "(posortowane wg końcowej tabeli, zielony=1., czerwony=18.)",
             fontsize=13, weight="bold")
fig.tight_layout(pad=2, rect=[0, 0, 1, 0.95])
save_figure(fig, "fig90_style_profiles_shape.png", output_dir=FIG_STYLE)
