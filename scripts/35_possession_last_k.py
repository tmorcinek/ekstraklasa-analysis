"""Skrypt 35: Posiadanie piłki w ostatnich k meczach per drużyna.

Funkcja plot_possession_last_k(teams, k) tworzy siatkę wykresów:
- jeden panel na drużynę
- słupki posiadania per mecz (chronologicznie)
- kolor słupka: zielony=wygrana, żółty=remis, czerwony=porażka
- linia 50% i rolling average
- tytuł: drużyna + siła rywala
"""
import _bootstrap  # noqa: F401

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.colors
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ekstraklasa.config import data_path, FIG_STYLE, CURRENT_SEASON, TEAM_MAP
from ekstraklasa.data.loaders import load_pol_season
from ekstraklasa.metrics.dixon_coles import fit_maher
from ekstraklasa.data.tables import build_league_table

SPARSE_COLS = ['Through balls', 'Errors lead to a goal', 'Red cards',
               'Penalty saves', 'Errors lead to a shot', 'Punches',
               'Big saves', 'High claims']


def load_stats() -> tuple[pd.DataFrame, dict, dict]:
    path = data_path("ekstraklasa_25_26_statistics.csv")
    df = pd.read_csv(path)
    drop = [c for c in SPARSE_COLS if c in df.columns]
    df = df.drop(columns=drop)
    df['team_short'] = df['team_name'].map(TEAM_MAP)
    df['opp_short']  = df['opposition_name'].map(TEAM_MAP)
    df['match_date'] = pd.to_datetime(df['match_date'])

    # Maher strength
    matches = load_pol_season(data_path("POL.csv"), CURRENT_SEASON)
    fit = fit_maher(matches)
    strength_map = {t: fit['att'][i] + fit['def'][i]
                    for i, t in enumerate(fit['teams'])}
    df['opp_strength'] = df['opp_short'].map(strength_map)

    # Final rank
    tbl = build_league_table("Ekstraklasa", matches)
    rank_map = {row['Team']: idx + 1
                for idx, row in tbl.reset_index(drop=True).iterrows()}

    return df, strength_map, rank_map


def plot_possession_last_k(
    teams: list[str],
    k: int,
    df: pd.DataFrame,
    rank_map: dict,
    metric: str = "Ball possession",
    ylabel: str = None,
    color_by: str = "result",   # "result" (W/D/L) lub "value" (gradient)
    cmap_value: str = "RdYlGn", # colormap dla trybu "value"
    ylim: tuple = None,         # (y_min, y_max) — nadpisuje automatyczną skalę
    ncols: int = 3,
    figsize_per_panel: tuple = (5, 3.5),
    title: str = "",
    save_path=None,
) -> plt.Figure:
    """
    Tworzy siatkę wykresów wybranej metryki w ostatnich k meczach.

    Parametry
    ---------
    teams       : lista nazw drużyn (skrócone, np. 'Lech Poznan')
    k           : liczba ostatnich meczów do pokazania
    df          : DataFrame ze stats (wynik load_stats())
    rank_map    : słownik team → pozycja w tabeli
    metric      : kolumna do wykresu (domyślnie 'Ball possession')
    ylabel      : etykieta osi Y (domyślnie = nazwa metryki)
    color_by    : 'result' — kolory wg W/D/L | 'value' — gradient wg wartości metryki
    cmap_value  : colormap dla trybu 'value' (domyślnie 'RdYlGn')
    ncols       : liczba kolumn w siatce
    figsize_per_panel : rozmiar jednego panelu w calach
    title       : nadtytuł wykresu
    save_path   : ścieżka do zapisu (None = nie zapisuje)

    Zwraca
    ------
    matplotlib.Figure
    """
    ylabel = ylabel or metric

    # Globalna skala Y — wspólna dla wszystkich paneli
    all_vals = []
    for team in teams:
        td = (df[df['team_short'] == team]
              .sort_values('match_date')
              .tail(k)[metric]
              .values.astype(float))
        all_vals.extend(td[~np.isnan(td)])
    if ylim is not None:
        y_min, y_max = ylim
    elif metric == "Ball possession":
        y_min, y_max = 0, 100
    else:
        v_min = np.nanmin(all_vals)
        v_max = np.nanmax(all_vals)
        margin = (v_max - v_min) * 0.12
        y_min = (v_min - margin) if v_min < 0 else 0
        y_max = v_max + margin

    n = len(teams)
    nrows = int(np.ceil(n / ncols))
    fig_w = figsize_per_panel[0] * ncols
    fig_h = figsize_per_panel[1] * nrows

    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(fig_w, fig_h),
                             facecolor="#f8f8f8")
    axes = np.array(axes).flatten()

    RESULT_COLORS = {
        'W': '#27ae60',   # wygrana — zielony
        'D': '#f0c040',   # remis — żółty
        'L': '#e05555',   # porażka — czerwony
    }

    for i, team in enumerate(teams):
        ax = axes[i]
        ax.set_facecolor("#f8f8f8")

        # Dane drużyny, posortowane chronologicznie, ostatnie k meczów
        td = (df[df['team_short'] == team]
              .sort_values('match_date')
              .tail(k)
              .reset_index(drop=True))

        if len(td) == 0:
            ax.set_visible(False)
            continue

        possession = td[metric].values.astype(float)
        x = np.arange(len(td))

        # Wynik meczu (zawsze liczymy, potrzebne do legendy i trybu result)
        def match_result(row):
            gs, gc = row['goals_scored'], row['goals_conceded']
            if gs > gc:   return 'W'
            elif gs < gc: return 'L'
            else:          return 'D'

        results = td.apply(match_result, axis=1).values

        if color_by == "value":
            # Gradient wg wartości — normalizacja do globalnego zakresu
            norm = matplotlib.colors.Normalize(vmin=y_min, vmax=y_max)
            cmap_obj = plt.get_cmap(cmap_value)
            bar_colors = [cmap_obj(norm(v)) if not np.isnan(v) else "#cccccc"
                          for v in possession]
        else:
            bar_colors = [RESULT_COLORS[r] for r in results]

        # Słupki
        bars = ax.bar(x, possession, color=bar_colors, alpha=0.80,
                      width=0.7, zorder=3)

        # Linia referencyjna: średnia drużyny z wyświetlanych meczów
        ref_val = np.nanmean(possession)
        ref_label = f"śr. {ref_val:.1f}"
        ax.axhline(ref_val, color="#444", linewidth=1.2, linestyle=":",
                   alpha=0.75, zorder=2, label=ref_label)

        # Rolling average (okno 5, min 3)
        if len(possession) >= 3:
            roll = pd.Series(possession).rolling(5, min_periods=3).mean().values
            ax.plot(x, roll, color="#2c3e50", linewidth=1.8,
                    linestyle="-", zorder=4, label="śr. krocząca (5)")

        # Oś X: etykiety rywali (skrócone) + symbol H/A
        labels = []
        for _, row in td.iterrows():
            opp = row['opp_short'] or ''
            opp_short = opp.split()[0][:5]
            ha = 'H' if row['is_home'] else 'A'
            labels.append(f"{opp_short}\n({ha})")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=6, rotation=0)

        # Tytuł panelu: drużyna + pozycja w tabeli
        rank = rank_map.get(team, '?')
        mean_val = np.nanmean(possession)
        unit = "%" if metric == "Ball possession" else ""
        ax.set_title(f"{rank}. {team}  |  śr. {mean_val:.1f}{unit}",
                     fontsize=9, fontweight="bold", pad=4)

        ax.set_ylim(y_min, y_max)
        if metric == "Ball possession":
            ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_ylabel(ylabel, fontsize=7.5)
        ax.grid(axis="y", alpha=0.25, zorder=1)

        # Wartości na słupkach (co 2 żeby nie tłoczyć)
        for j, (bar, v) in enumerate(zip(bars, possession)):
            if j % 2 == 0 and not np.isnan(v):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        v + 1.5, f"{v:.0f}",
                        ha="center", fontsize=6, color="#333")

    # Ukryj nadmiarowe panele
    for j in range(n, len(axes)):
        axes[j].set_visible(False)

    # Legenda / colorbar
    from matplotlib.patches import Patch
    if color_by == "value":
        # Colorbar na dole figury
        cax = fig.add_axes([0.15, -0.02, 0.70, 0.015])
        norm = matplotlib.colors.Normalize(vmin=y_min, vmax=y_max)
        sm = plt.cm.ScalarMappable(cmap=cmap_value, norm=norm)
        sm.set_array([])
        cb = fig.colorbar(sm, cax=cax, orientation="horizontal")
        cb.set_label(ylabel, fontsize=9)
    else:
        legend_handles = [
            Patch(facecolor=RESULT_COLORS['W'], alpha=0.8, label='Wygrana'),
            Patch(facecolor=RESULT_COLORS['D'], alpha=0.8, label='Remis'),
            Patch(facecolor=RESULT_COLORS['L'], alpha=0.8, label='Porażka'),
        ]
        fig.legend(handles=legend_handles, loc="lower center",
                   ncol=3, fontsize=9, framealpha=0.8,
                   bbox_to_anchor=(0.5, -0.01))

    suptitle = title or f"Posiadanie piłki — ostatnie {k} meczów"
    fig.suptitle(suptitle, fontsize=12, fontweight="bold", y=1.01)
    plt.tight_layout(pad=1.5)

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Saved {save_path}")

    return fig


# ── Przykład: top 9 drużyn, ostatnie 18 meczów ───────────────────────────────

def main():
    print("Wczytywanie danych...")
    df, strength_map, rank_map = load_stats()

    # fig66: Top 9 drużyn wg końcowej tabeli, ostatnie 18 meczów
    top9 = sorted(rank_map, key=rank_map.get)[:9]
    print(f"Top 9: {top9}")

    plot_possession_last_k(
        teams=top9,
        k=18,
        df=df,
        rank_map=rank_map,
        ncols=3,
        figsize_per_panel=(5.5, 3.8),
        title="Posiadanie piłki — 9 najlepszych drużyn, ostatnie 18 meczów\n"
              "(kolor słupka: zielony=W, żółty=D, czerwony=L)",
        save_path=FIG_STYLE / "fig66_possession_top9_last18.png",
    )

    # fig66b: Lech Poznań — wszystkie mecze sezonu
    lech = "Lech Poznan"
    k_all = len(df[df["team_short"] == lech])
    plot_possession_last_k(
        teams=[lech],
        k=k_all,
        df=df,
        rank_map=rank_map,
        ncols=1,
        figsize_per_panel=(10, 4.5),
        title="Posiadanie piłki Lecha Poznań w każdym meczu sezonu (2025/26)\n"
              "(kolor słupka: zielony=W, żółty=D, czerwony=L)",
        save_path=FIG_STYLE / "fig66b_possession_lech_all.png",
    )


if __name__ == "__main__":
    main()
