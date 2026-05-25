import math
import numpy as np
import pandas as pd


def gini(values: np.ndarray) -> float:
    """Standard Gini coefficient (0 = perfect equality, 1 = max inequality)."""
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return float("nan")
    if np.amin(arr) < 0:
        arr = arr - np.amin(arr)
    arr = np.sort(arr) + 1e-12
    n = arr.size
    idx = np.arange(1, n + 1)
    return float((np.sum((2 * idx - n - 1) * arr)) / (n * np.sum(arr)))


def hhi_normalized(values: np.ndarray) -> float:
    """Normalized Herfindahl-Hirschman index. 0 = perfect equality, 1 = single team dominates."""
    arr = np.asarray(values, dtype=float)
    shares = arr / arr.sum()
    h = np.sum(shares ** 2)
    n = len(arr)
    return float((h - 1 / n) / (1 - 1 / n))


def isd_points_with_draws(n_games_per_team: float, draw_rate: float) -> float:
    """ISD adjusted for empirical draw rate q (3-1-0 system).

    Per-match Var(points) under p_w = (1-q)/2: E[X²] - E[X]², expanded for {3,1,0}.
    """
    p_w = (1 - draw_rate) / 2
    e_x = 3 * p_w + 1 * draw_rate
    e_x2 = 9 * p_w + 1 * draw_rate
    var_per_match = e_x2 - e_x ** 2
    return math.sqrt(var_per_match * n_games_per_team)


def noll_scully(points: np.ndarray, n_games_per_team: float, draw_rate: float = 0.25) -> float:
    """Noll-Scully with draw-corrected ISD (default q=0.25 as football benchmark)."""
    return float(np.std(points, ddof=0)) / isd_points_with_draws(n_games_per_team, draw_rate)


def entropy_wdl(matches: pd.DataFrame) -> float:
    """Shannon entropy (bits) of W/D/L outcome distribution."""
    counts = matches["Res"].value_counts(normalize=True)
    probs = np.array([counts.get(key, 0.0) for key in ("H", "D", "A")])
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log2(probs)))


def distribution_stats(points: np.ndarray, n_games_per_team: float, draw_rate: float = 0.25) -> dict:
    """Mean, ASD, NS (draw-corrected, q=0.25 default), skewness γ₁, excess kurtosis γ₂, min/max/range/median."""
    arr = np.array(points, dtype=float)
    mu = arr.mean()
    m2 = np.mean((arr - mu) ** 2)
    m3 = np.mean((arr - mu) ** 3)
    m4 = np.mean((arr - mu) ** 4)
    std = math.sqrt(m2)
    isd = isd_points_with_draws(n_games_per_team, draw_rate)
    return {
        "N_teams": len(arr),
        "N_games": n_games_per_team,
        "Mean_pts": round(mu, 2),
        "Median_pts": round(float(np.median(arr)), 2),
        "ASD": round(std, 2),
        "ISD": round(isd, 2),
        "NS": round(std / isd, 3),
        "Min": int(arr.min()),
        "Max": int(arr.max()),
        "Range": int(arr.max() - arr.min()),
        "Skewness": round(m3 / (m2 ** 1.5), 3) if m2 > 0 else 0.0,
        "Exc_Kurtosis": round(m4 / (m2 ** 2) - 3, 3) if m2 > 0 else 0.0,
    }
