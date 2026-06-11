"""Wizualizacje macierzy bezpośrednich pojedynków (head-to-head).

Warstwa wizualizacji — przyjmuje gotowe macierze punktów (DataFrame) i odczyty.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ekstraklasa.config import FIG_LEAGUES
from ekstraklasa.plots.style import save_figure


def _draw_h2h_panel(ax, matrix: pd.DataFrame, title: str) -> None:
    values = matrix.values
    n_teams = len(matrix)
    im = ax.imshow(np.ma.masked_invalid(values), cmap="Greens",
                   aspect="equal", vmin=0, vmax=6)
    positions = [str(i + 1) for i in range(n_teams)]
    ax.set_xticks(range(n_teams))
    ax.set_yticks(range(n_teams))
    ax.set_xticklabels(positions, fontsize=7)
    ax.set_yticklabels(positions, fontsize=7)
    ax.set_xlabel("przeciwnik (pozycja w tabeli)", fontsize=10)
    ax.set_title(title, fontsize=12, weight="bold")
    ax.tick_params(length=0)
    return im


def fig_h2h_side_by_side(matrices: dict[str, pd.DataFrame],
                         cyclic_rates: dict[str, float],
                         filename: str,
                         *,
                         title: str,
                         output_dir: Path = FIG_LEAGUES) -> None:
    """1xN macierzy punktów H2H obok siebie (numery pozycji, wspólna skala 0–6)."""
    leagues = list(matrices)
    fig, axes = plt.subplots(1, len(leagues), figsize=(5.4 * len(leagues), 5.6))

    im = None
    for ax, league in zip(axes, leagues):
        panel_title = f"{league}\ncykle {cyclic_rates[league] * 100:.0f}%"
        im = _draw_h2h_panel(ax, matrices[league], panel_title)

    axes[0].set_ylabel("drużyna (pozycja w tabeli)", fontsize=10)
    fig.suptitle(title, fontsize=14, weight="bold")
    cbar = fig.colorbar(im, ax=axes, shrink=0.6, pad=0.02)
    cbar.set_label("punkty zdobyte z rywalem (0–6)", fontsize=9)
    save_figure(fig, filename, output_dir=output_dir)
