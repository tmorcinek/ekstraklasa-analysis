import numpy as np
import matplotlib.pyplot as plt

from ekstraklasa.config import COLORS, ALL_SIX
from ekstraklasa.plots.style import save_figure, clean_axes


def fig6_mc_distributions(sim_data: dict) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharey=False)
    for ax, name in zip(axes.flat, ALL_SIX):
        data = sim_data[name]
        sim_asd = data["sim_asd"]
        obs_asd = data["obs_asd"]
        ax.hist(sim_asd, bins=40, color=COLORS[name], alpha=0.7, edgecolor="white")
        ax.axvline(obs_asd, color="black", linewidth=2.2)
        pct = (sim_asd <= obs_asd).mean() * 100
        ax.text(0.97, 0.95, f"obserwowane ASD = {obs_asd:.1f}\nP(sim ≤ obs) = {pct:.1f}%",
                transform=ax.transAxes, ha="right", va="top", fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="gray"))
        ax.set_title(name, fontsize=12, weight="bold")
        ax.set_xlabel("Symulowane końcowe ASD")
        ax.set_ylabel("Liczba")
        clean_axes(ax)
    fig.suptitle("Monte Carlo: gdzie znajduje się rzeczywiste ASD w rozkładzie modelu?",
                 fontsize=14, weight="bold", x=0.02, ha="left")
    fig.tight_layout(rect=[0, 0.02, 1, 0.96])
    save_figure(fig, "fig6_mc_asd_distributions.png")


def fig7_team_strengths(sim_data: dict) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    for row, name in enumerate(ALL_SIX):
        strength = sim_data[name]["strength"]
        jitter = (np.full_like(strength, row, dtype=float)
                  + np.random.RandomState(7).uniform(-0.18, 0.18, size=len(strength)))
        ax.scatter(strength, jitter, color=COLORS[name], s=80, edgecolor="white", linewidth=1, zorder=3)
        mean = strength.mean()
        std = strength.std()
        ax.errorbar([mean], [row], xerr=[std], color="black", capsize=6, fmt="o",
                    markerfacecolor="black", markersize=4, zorder=4)
        ax.text(mean + std + 0.02, row, f"SD={std:.2f}", va="center", fontsize=8, color="black")
    ax.set_yticks(range(len(ALL_SIX)))
    ax.set_yticklabels(ALL_SIX)
    ax.set_xlabel("Klasa drużyny = siła ataku + siła obrony (skala logarytmiczna)")
    ax.set_title("Jak duże jest realne zróżnicowanie klas drużyn w każdej lidze?",
                 fontsize=14, weight="bold", loc="left", pad=14)
    ax.grid(axis="x", alpha=0.3)
    clean_axes(ax)
    fig.text(0.99, 0.01,
             "czarne słupki: ±1 odchylenie standardowe klas drużyn",
             ha="right", fontsize=8, color="gray")
    fig.tight_layout()
    save_figure(fig, "fig7_team_strengths.png")
