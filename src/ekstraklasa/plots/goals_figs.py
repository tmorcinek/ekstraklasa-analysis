from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from ekstraklasa.config import COLORS, LEAGUES, FIG_TEAMS, FIG_BALANCE
from ekstraklasa.plots.style import save_figure, clean_axes


def _draw_goal_diff_panel(ax, title: str, dist: pd.Series, color: str,
                          y_max: float, max_diff: int) -> None:
    x_values = list(dist.index)
    heights = dist.values * 100
    bars = ax.bar(x_values, heights, color=color, edgecolor="black", linewidth=0.5)

    for bar, height in zip(bars, heights):
        ax.text(bar.get_x() + bar.get_width() / 2, height + y_max * 0.02,
                f"{height:.1f}%", ha="center", va="bottom", fontsize=9)

    ax.set_title(title, fontsize=12, weight="bold")
    ax.set_xlabel("Różnica bramkowa", fontsize=10)
    ax.set_ylabel("% meczów", fontsize=10)
    ax.set_xticks(x_values)
    ax.set_xticklabels([f"{x}+" if x == max_diff else str(x) for x in x_values])
    ax.set_ylim(0, y_max * 1.18)
    ax.grid(axis="y", alpha=0.3)
    clean_axes(ax)


def fig21_goal_diff_distributions(distributions: dict[str, pd.Series],
                                   max_diff: int = 5) -> None:
    """6-panel (2x3) bar chart: share of matches by |goal diff|, one league per panel."""
    leagues = list(LEAGUES.keys())
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes_flat = axes.flatten()

    y_max = max(dist.max() for dist in distributions.values()) * 100

    for i, league in enumerate(leagues):
        _draw_goal_diff_panel(axes_flat[i], league, distributions[league],
                              COLORS[league], y_max, max_diff)

    fig.suptitle("Rozkład meczów wg różnicy bramkowej (2025/26)",
                 fontsize=14, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    save_figure(fig, "fig21_goal_diff_distribution.png", output_dir=FIG_TEAMS)


def fig_goal_diff_side_by_side(distributions: dict[str, pd.Series],
                               colors: dict[str, str],
                               filename: str,
                               *,
                               title: str,
                               output_dir: Path = FIG_BALANCE,
                               max_diff: int = 5) -> None:
    """1xN bar chart of |goal diff| share, one league per panel, shared y-scale."""
    leagues = list(distributions)
    fig, axes = plt.subplots(1, len(leagues), figsize=(4.7 * len(leagues), 4.6))
    y_max = max(dist.max() for dist in distributions.values()) * 100

    for ax, league in zip(axes, leagues):
        _draw_goal_diff_panel(ax, league, distributions[league],
                              colors[league], y_max, max_diff)

    fig.suptitle(title, fontsize=14, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save_figure(fig, filename, output_dir=output_dir)
