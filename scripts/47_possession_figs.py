"""Posiadanie a wynik — dwie figury do rozdziału „Kto ma piłkę, ten goni".
- fig116: odsetek zwycięstw drużyny z piłką wg progu posiadania (3 ligi, linie).
- fig117: mediana czasu na prowadzeniu wg przedziału posiadania (3 ligi, panele).
Dane wejściowe: data/{slug}_{statistics_all,progress}.csv (snapshot 2025/26).
Output: figures/leagues/.
"""
import _bootstrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ekstraklasa.config import FIG_LEAGUES, COLORS, data_path
from ekstraklasa.plots.style import save_figure, clean_axes
LEAGUES = {
    "Ekstraklasa": ("ekstraklasa", COLORS["Ekstraklasa"]),
    "EPL": ("premier-league", COLORS["EPL"]),
    "Liga Portugal": ("liga-portugal-betclic", "#2e7d32"),
}
THRESHOLDS = [51, 55, 60, 65, 70]
POSSESSION_BANDS = [0, 40, 45, 50, 55, 60, 65, 100]
BAND_LABELS = ["<40", "40-45", "45-50", "50-55", "55-60", "60-65", "65+"]


def win_pct_by_threshold(stats: pd.DataFrame) -> pd.Series:
    won = stats["goals_scored"] > stats["goals_conceded"]
    rows = {}
    for threshold in THRESHOLDS:
        dominant = stats[stats["Ball possession"] >= threshold]
        rows[threshold] = 100 * won[dominant.index].mean() if len(dominant) else 0.0
    return pd.Series(rows)


def leading_by_possession(slug: str) -> pd.DataFrame:
    progress = pd.read_csv(data_path(f"{slug}_progress.csv")).set_index("match_id")
    progress = progress[(progress["home_score"] != 0) | (progress["away_score"] != 0)]
    stats = pd.read_csv(data_path(f"{slug}_statistics_all.csv"))
    home_possession = stats[stats["is_home"]].set_index("match_id")["Ball possession"]
    away_possession = stats[~stats["is_home"]].set_index("match_id")["Ball possession"]
    home = pd.DataFrame({"leading_pct": progress["home_leading_pct"], "possession": home_possession})
    away = pd.DataFrame({"leading_pct": progress["away_leading_pct"], "possession": away_possession})
    return pd.concat([home, away], ignore_index=True).dropna(subset=["leading_pct", "possession"])


def median_leading_by_band(df: pd.DataFrame) -> pd.Series:
    band = pd.cut(df["possession"], bins=POSSESSION_BANDS, labels=BAND_LABELS, right=False)
    return df.groupby(band, observed=False)["leading_pct"].median()


statistics = {league: pd.read_csv(data_path(f"{slug}_statistics_all.csv"))
              for league, (slug, _) in LEAGUES.items()}

# ── fig116: odsetek zwycięstw wg progu posiadania ─────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
for league, (_, color) in LEAGUES.items():
    win_pct = win_pct_by_threshold(statistics[league])
    ax.plot(win_pct.index, win_pct.values, marker="o", linewidth=2, color=color, label=league)
ax.set_xticks(THRESHOLDS)
ax.set_xlabel("Minimalne posiadanie piłki (%)", fontsize=11)
ax.set_ylabel("Odsetek zwycięstw (%)", fontsize=11)
ax.set_title("Odsetek zwycięstw drużyny z piłką wg progu posiadania (2025/26)",
             fontsize=12, weight="bold")
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
clean_axes(ax)
fig.tight_layout()
save_figure(fig, "fig116_possession_win_pct_leagues.png", output_dir=FIG_LEAGUES)

# ── fig117: mediana czasu na prowadzeniu wg przedziału posiadania ──────────────
medians = {league: median_leading_by_band(leading_by_possession(slug))
           for league, (slug, _) in LEAGUES.items()}

fig, axes = plt.subplots(1, len(LEAGUES), figsize=(14, 4.8), sharey=True)
for ax, (league, (_, color)) in zip(axes, LEAGUES.items()):
    series = medians[league]
    ax.bar(BAND_LABELS, series.reindex(BAND_LABELS).values, color=color,
           edgecolor="black", linewidth=0.5)
    ax.set_title(league, fontsize=12, weight="bold")
    ax.set_xlabel("Przedział posiadania (%)", fontsize=10)
    ax.tick_params(axis="x", labelrotation=45)
    ax.grid(axis="y", alpha=0.3)
    clean_axes(ax)
axes[0].set_ylabel("Mediana czasu na prowadzeniu (% meczu)", fontsize=10)
fig.suptitle("Mediana czasu na prowadzeniu wg przedziału posiadania — trzy ligi (2025/26)",
             fontsize=14, weight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95])
save_figure(fig, "fig117_possession_band_median_leagues.png", output_dir=FIG_LEAGUES)
