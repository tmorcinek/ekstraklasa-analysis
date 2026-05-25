import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from ekstraklasa.plots.style import save_figure

BLACK = np.array(mcolors.to_rgb("#222222"))
GREEN = np.array(mcolors.to_rgb("#1a8a1a"))
RED = np.array(mcolors.to_rgb("#cc2222"))


def _delta_color(delta: int) -> tuple[float, float, float]:
    """Square-root gradient: black at delta=0, saturating green/red at ±10."""
    t = min(np.sqrt(abs(delta) / 10.0), 1.0)
    target = GREEN if delta >= 0 else RED
    return tuple((1 - t) * BLACK + t * target)


def _draw_slope_chart(rows: list[dict], *,
                      n_teams: int,
                      prev_season: str,
                      curr_season: str,
                      mean_label: str,
                      footnote: str | None,
                      league_title: str,
                      output_name: str) -> None:
    """Render a slope chart from pre-built rows.

    Each row: {"name": str, "prev": int, "curr": int, "left_label": str}.
    """
    fig, ax = plt.subplots(figsize=(9, 11))
    ax.set_xlim(-0.3, 1.3)
    ax.set_ylim(n_teams + 0.8, 0.2)

    x_left, x_right, pad = 0.0, 1.0, 0.04

    for row in rows:
        name = row["name"]
        pos_prev, pos_cur = row["prev"], row["curr"]
        delta = pos_prev - pos_cur
        color = _delta_color(delta)
        ax.plot([x_left, x_right], [pos_prev, pos_cur], color=color, lw=2.0,
                solid_capstyle="round", zorder=3)
        ax.scatter([x_left, x_right], [pos_prev, pos_cur], color=color, s=50, zorder=4)
        delta_label = str(delta) if delta != 0 else "0"
        ax.text(0.5, (pos_prev + pos_cur) / 2, delta_label,
                ha="center", va="center", fontsize=7.0, color=color, weight="bold",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85),
                zorder=5)
        ax.text(x_left - pad, pos_prev, row["left_label"],
                ha="right", va="center", fontsize=8.2, color=color)
        ax.text(x_right + pad, pos_cur, f"{pos_cur}. {name}",
                ha="left", va="center", fontsize=8.2, color=color)

    ax.text(x_left, 0.0, prev_season, ha="center", va="bottom",
            fontsize=10, weight="bold", color="#333333")
    ax.text(x_right, 0.0, curr_season, ha="center", va="bottom",
            fontsize=10, weight="bold", color="#333333")
    ax.text(0.5, n_teams + 1.1, mean_label,
            ha="center", va="top", fontsize=8.5, color="#555555", style="italic")
    if footnote:
        ax.text(0.0, n_teams + 1.5, footnote,
                ha="left", va="top", fontsize=7, color="#888888", style="italic")

    ax.axis("off")
    fig.suptitle(league_title, fontsize=13, weight="bold", x=0.5, y=0.99)
    fig.tight_layout(rect=[0, 0.03, 1, 0.98])
    save_figure(fig, output_name, bbox_inches="tight")


def fig_slope_chart(changes: pd.DataFrame, *,
                    league_name: str,
                    prev_season: str,
                    curr_season: str,
                    output_name: str,
                    name_map: dict[str, str] | None = None) -> None:
    """Slope chart of team positions between two seasons.

    changes: DataFrame from position_changes() with Team/PrevRank/CurrRank/Kind.
    name_map: optional {raw_name: display_name} — for renaming teams (e.g. adding
              Polish diacritics when source data uses ASCII).
    """
    name_map = name_map or {}
    rows = []
    for _, change_row in changes.iterrows():
        raw_name = change_row["Team"]
        display_name = name_map.get(raw_name, raw_name)
        prev = int(change_row["PrevRank"])
        curr = int(change_row["CurrRank"])
        is_promoted = change_row["Kind"] == "promoted"
        left_label = f"—  {display_name}" if is_promoted else f"{prev}. {display_name}"
        rows.append({"name": display_name, "prev": prev, "curr": curr,
                     "left_label": left_label})

    mean_abs = float(changes["AbsDiff"].mean())
    n_teams = len(changes)
    promoted_prev_ranks = sorted(int(r["PrevRank"]) for _, r in changes.iterrows()
                                  if r["Kind"] == "promoted")
    if promoted_prev_ranks:
        ranks_str = ", ".join(str(rank) for rank in promoted_prev_ranks)
        footnote = (f"— beniaminkowie {curr_season} "
                    f"(do średniej przypisani pozycjom {ranks_str} z {prev_season})")
    else:
        footnote = None

    _draw_slope_chart(
        rows,
        n_teams=n_teams,
        prev_season=prev_season,
        curr_season=curr_season,
        mean_label=f"Średnia zmiana pozycji: {mean_abs:.1f} miejsca",
        footnote=footnote,
        league_title=f"{league_name} — zmiany pozycji między sezonami",
        output_name=output_name,
    )
