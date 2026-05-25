import numpy as np
import pandas as pd

from ekstraklasa.metrics.odds import select_odds_source, probabilities_matrix


def get_probs_and_outcomes(matches: pd.DataFrame, min_rows: int = 30) -> tuple[np.ndarray | None, np.ndarray | None, int, str]:
    """Probabilities + actual outcomes using best odds source. Returns (P, y, n, src_label)."""
    chosen = select_odds_source(matches, min_rows=min_rows)
    if chosen is None:
        return None, None, 0, "none"
    probs, outcomes = probabilities_matrix(matches, chosen)
    return probs, outcomes, len(outcomes), chosen[0]


def murphy_decomposition(probs: np.ndarray, outcomes: np.ndarray, n_bins: int = 10) -> dict:
    """Decompose Brier = Reliability − Resolution + Uncertainty for favourite-wins binary problem."""
    n = len(outcomes)
    onehot = np.zeros_like(probs)
    onehot[np.arange(n), outcomes] = 1
    brier_multi = float(np.mean(np.sum((probs - onehot) ** 2, axis=1)))

    p_max = probs.max(axis=1)
    favourite = probs.argmax(axis=1)
    fav_won = (favourite == outcomes).astype(float)

    bins = np.linspace(p_max.min() - 1e-6, p_max.max() + 1e-6, n_bins + 1)
    bin_idx = np.digitize(p_max, bins) - 1

    base_rate = fav_won.mean()
    reliability = 0.0
    resolution = 0.0
    for bin_id in range(n_bins):
        mask = bin_idx == bin_id
        size = mask.sum()
        if size == 0:
            continue
        pred = p_max[mask].mean()
        obs = fav_won[mask].mean()
        reliability += (size / n) * (pred - obs) ** 2
        resolution += (size / n) * (obs - base_rate) ** 2
    uncertainty = base_rate * (1 - base_rate)

    return {
        "brier_multiclass": brier_multi,
        "brier_favwin": reliability - resolution + uncertainty,
        "reliability": reliability,
        "resolution": resolution,
        "uncertainty": uncertainty,
        "fav_winrate": base_rate,
    }
