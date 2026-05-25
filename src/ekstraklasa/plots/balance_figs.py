import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from ekstraklasa.config import COLORS, ALL_SIX, TOP5
from ekstraklasa.data.tables import build_table
from ekstraklasa.metrics.balance import isd_points_with_draws
from ekstraklasa.plots.style import save_figure, clean_axes


def fig3_noll_scully(leagues: dict[str, dict]) -> None:
    rows = []
    for name in ALL_SIX:
        table = leagues[name]["table"]
        n_games = table["P"].mean()
        ns = float(np.std(table["Pts"].values, ddof=0)) / isd_points_with_draws(n_games, 0.25)
        rows.append((name, ns))
    rows.sort(key=lambda r: r[1])
    names = [r[0] for r in rows]
    values = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.barh(names, values, color=[COLORS[n] for n in names], edgecolor="black", linewidth=0.5)
    ax.axvline(1.0, color="black", linestyle="--", linewidth=1.2, alpha=0.7)
    ax.text(1.0, len(names) - 0.4, " 1.0 = liga losowa",
            color="black", fontsize=9, va="center")
    for bar, value in zip(bars, values):
        ax.text(value + 0.03, bar.get_y() + bar.get_height() / 2, f"{value:.2f}",
                va="center", fontsize=10)
    ax.set_xlabel("Noll-Scully (ASD / ISD)", fontsize=11)
    ax.set_title("Jak rozwarstwione są ligi? (wyższe = silniejsza hierarchia)",
                 fontsize=13, weight="bold", loc="left", pad=14)
    ax.grid(axis="x", alpha=0.3)
    clean_axes(ax)
    fig.tight_layout()
    save_figure(fig, "fig3_nollscully_2526.png")


def fig17_asd_compare(leagues: dict[str, dict]) -> None:
    """ASD comparison: Ekstraklasa vs Top 5 (2025/26)."""
    rows = []
    for name in ALL_SIX:
        table = leagues[name]["table"]
        asd = float(np.std(table["Pts"].values, ddof=0))
        rows.append((name, asd))
    rows.sort(key=lambda r: r[1])
    names = [r[0] for r in rows]
    values = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.barh(names, values, color=[COLORS[n] for n in names], edgecolor="black", linewidth=0.5)
    for bar, value in zip(bars, values):
        ax.text(value + 0.3, bar.get_y() + bar.get_height() / 2, f"{value:.1f}",
                va="center", fontsize=10)
    ax.set_xlabel("ASD — odchylenie standardowe punktów", fontsize=11)
    ax.set_title("ASD punktów: Ekstraklasa vs Top 5 (2025/26)",
                 fontsize=13, weight="bold", loc="left", pad=14)
    ax.grid(axis="x", alpha=0.3)
    clean_axes(ax)
    fig.tight_layout()
    save_figure(fig, "fig17_asd_compare.png")


def fig18_ns_history(pol_all: pd.DataFrame, leagues: dict[str, dict]) -> None:
    """Noll-Scully history of Ekstraklasa with threshold line at NS = 1.0."""
    seasons = sorted(pol_all["Season"].unique())
    ns_vals = []
    for season in seasons:
        table = build_table(pol_all[pol_all["Season"] == season])
        pts = table["Pts"].values
        n_games = table["P"].mean()
        asd = float(np.std(pts, ddof=0))
        ns = asd / isd_points_with_draws(n_games, 0.25)
        ns_vals.append(ns)

    top5_ns = []
    for name in TOP5:
        table = leagues[name]["table"]
        pts = table["Pts"].values
        n_games = table["P"].mean()
        asd = float(np.std(pts, ddof=0))
        ns = asd / isd_points_with_draws(n_games, 0.25)
        top5_ns.append(ns)
    top5_mean = np.mean(top5_ns)

    fig, ax = plt.subplots(figsize=(11, 5.5))
    short = [s.replace("/20", "/")[:7] for s in seasons]
    ax.plot(short, ns_vals, marker="o", color=COLORS["Ekstraklasa"], linewidth=2.4, markersize=8, zorder=3)
    current_idx = seasons.index("2025/2026")
    ax.scatter([short[current_idx]], [ns_vals[current_idx]], color=COLORS["Ekstraklasa"], s=240,
               edgecolor="black", linewidth=2, zorder=4)
    ax.annotate(f"  2025/26: NS = {ns_vals[current_idx]:.2f}",
                xy=(short[current_idx], ns_vals[current_idx]),
                xytext=(short[current_idx], ns_vals[current_idx] - 0.18),
                fontsize=11, weight="bold", ha="center")

    ax.axhline(1.0, color="black", linestyle="--", linewidth=1.4, alpha=0.85)
    ax.text(short[-1], 1.02, "NS = 1.0 (liga losowa)",
            color="black", fontsize=9, va="bottom", ha="right")

    ax.axhline(top5_mean, color="gray", linestyle=":", linewidth=1.2, alpha=0.7)
    ax.text(short[0], top5_mean + 0.03, f"Średnia Top 5 (2025/26): {top5_mean:.2f}",
            color="gray", fontsize=9, va="bottom")

    ax.set_ylabel("Noll-Scully (NS)", fontsize=11)
    ax.set_title("Ekstraklasa: Noll-Scully w kolejnych sezonach",
                 fontsize=13, weight="bold", loc="left", pad=14)
    ax.grid(axis="y", alpha=0.3)
    clean_axes(ax)
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    fig.tight_layout()
    save_figure(fig, "fig18_ns_history.png")


def fig20_position_rotation(rotation: dict[str, float], highlight: str = "Ekstraklasa") -> None:
    """Vertical bar chart: avg position change between 2024/25 and 2025/26, all 6 leagues."""
    pairs = sorted(rotation.items(), key=lambda kv: kv[1], reverse=True)
    names = [name for name, _ in pairs]
    values = [value for _, value in pairs]
    gray = np.array(mcolors.to_rgb("#c8c5bf"))

    def muted(hex_color: str, mix: float = 0.85) -> tuple[float, float, float]:
        original = np.array(mcolors.to_rgb(hex_color))
        return tuple((1 - mix) * original + mix * gray)

    colors = [COLORS[name] if name == highlight else muted(COLORS[name]) for name in names]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.bar(names, values, color=colors, edgecolor="black", linewidth=0.6)

    y_max = max(values)
    for bar, value, name in zip(bars, values, names):
        weight = "bold" if name == highlight else "regular"
        ax.text(bar.get_x() + bar.get_width() / 2, value + y_max * 0.015,
                f"{value:.2f}", ha="center", va="bottom",
                fontsize=11, fontweight=weight)

    for tick_label in ax.get_xticklabels():
        if tick_label.get_text() == highlight:
            tick_label.set_fontweight("bold")
            tick_label.set_color(COLORS[highlight])

    ax.set_ylabel("Średnia |zmiana pozycji| 2024/25 → 2025/26", fontsize=11)
    ax.set_ylim(0, y_max * 1.18)
    ax.set_title("Rotacja pozycji między sezonami — 6 lig europejskich",
                 fontsize=13, weight="bold", loc="left", pad=14)
    ax.grid(axis="y", alpha=0.3)
    clean_axes(ax)
    fig.tight_layout()
    save_figure(fig, "fig20_position_rotation.png")
