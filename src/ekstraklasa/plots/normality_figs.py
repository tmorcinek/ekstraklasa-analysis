import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from ekstraklasa.config import LEAGUES
from ekstraklasa.metrics.balance import isd_points_with_draws
from ekstraklasa.metrics.normal import normal_pdf_scaled
from ekstraklasa.plots.style import save_figure, clean_axes


def fig14_eks_vs_bun_v2(pts_eks: np.ndarray, pts_bun: np.ndarray) -> None:
    x_min, x_max, bin_width = 10, 100, 5
    bins = np.arange(x_min, x_max + bin_width, bin_width)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)

    for ax, points, color, name, n_games in [
        (axes[0], pts_eks, "#d62728", "Ekstraklasa 2025/26", 34),
        (axes[1], pts_bun, "#2a6f70", "Bundesliga 2025/26", 34),
    ]:
        mu = float(points.mean())
        sigma = float(points.std(ddof=0))
        ax.hist(points, bins=bins, color=color, alpha=0.72,
                edgecolor="white", linewidth=1.1, zorder=2)
        x = np.linspace(bins[0], bins[-1], 400)
        ax.plot(x, normal_pdf_scaled(x, mu, sigma, len(points), bin_width),
                color="black", linewidth=2.0, zorder=4)
        ax.axvline(mu, color="black", linestyle=":", linewidth=1.4, alpha=0.7)
        ax.set_title(name, fontsize=11, weight="bold", loc="left", pad=4)
        m2 = float(np.mean((points - mu) ** 2))
        m3 = float(np.mean((points - mu) ** 3))
        skew = m3 / (m2 ** 1.5) if m2 > 0 else 0.0
        ax.text(0.97, 0.93, f"skośność = {skew:+.2f}", transform=ax.transAxes,
                ha="right", va="top", fontsize=9, color="black",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="gray", alpha=0.8))
        ax.set_xlabel("Punkty na koniec sezonu", fontsize=9)
        ax.set_xlim(bins[0], bins[-1])
        ax.grid(axis="y", alpha=0.25)
        clean_axes(ax)
        for point in points:
            ax.plot([point], [0.08], marker="|", color="black",
                    markersize=9, markeredgewidth=1.5, zorder=5)
    axes[0].set_ylabel("Liczba drużyn", fontsize=9)

    fig.suptitle("Rozkład punktów drużyn: Ekstraklasa vs Bundesliga",
                 fontsize=14, weight="bold", x=0.02, ha="left")
    fig.tight_layout(rect=[0, 0.04, 1, 0.95])
    save_figure(fig, "fig14_normality_eks_epl.png")


def fig15_all_leagues_grid(tables: dict[str, pd.DataFrame], stats_df: pd.DataFrame) -> None:
    league_order = ["Ekstraklasa", "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1"]
    bin_width = 5
    bins = np.arange(10, 105, bin_width)

    fig = plt.figure(figsize=(16, 9))
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.28)

    for idx, name in enumerate(league_order):
        row, col = divmod(idx, 3)
        ax = fig.add_subplot(gs[row, col])
        points = tables[name]["Pts"].values
        mu = float(points.mean())
        sigma = float(points.std(ddof=0))
        color = LEAGUES[name]["color"]
        n_games = LEAGUES[name]["games"]
        ns_val = sigma / isd_points_with_draws(n_games, 0.25)

        ax.hist(points, bins=bins, color=color, alpha=0.72,
                edgecolor="white", linewidth=1.0, zorder=2)
        x = np.linspace(bins[0], bins[-1], 400)
        ax.plot(x, normal_pdf_scaled(x, mu, sigma, len(points), bin_width),
                color="black", linewidth=1.8, zorder=4)
        ax.axvline(mu, color="black", linestyle=":", linewidth=1.2, alpha=0.65)

        skew = stats_df.loc[name, "Skewness"]
        info = f"skośność = {skew:+.2f}"
        ax.text(0.97, 0.97, info, transform=ax.transAxes,
                ha="right", va="top", fontsize=8, family="monospace",
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.85))

        ax.set_title(name, fontsize=11, weight="bold", loc="left", pad=3)
        ax.set_xlabel("Punkty", fontsize=8)
        if col == 0:
            ax.set_ylabel("Liczba drużyn", fontsize=8)
        ax.set_xlim(bins[0], bins[-1])
        ax.set_ylim(0, 8)
        ax.tick_params(labelsize=8)
        ax.grid(axis="y", alpha=0.2)
        clean_axes(ax)
        for point in points:
            ax.plot([point], [0.06], marker="|", color="black",
                    markersize=7, markeredgewidth=1.2, zorder=5)

    fig.suptitle("Rozkład punktów — 6 lig europejskich 2025/26",
                 fontsize=15, weight="bold", x=0.02, ha="left", y=0.98)
    save_figure(fig, "fig15_all_leagues_dist.png", bbox_inches="tight")
