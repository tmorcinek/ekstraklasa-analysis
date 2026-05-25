import numpy as np


def normal_pdf(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    return np.exp(-(x - mu) ** 2 / (2 * sigma ** 2)) / (sigma * np.sqrt(2 * np.pi))


def normal_pdf_scaled(x: np.ndarray, mu: float, sigma: float, sample_size: int, bin_width: float) -> np.ndarray:
    """Normal PDF scaled to match a histogram of `sample_size` observations and given bin width."""
    return normal_pdf(x, mu, sigma) * sample_size * bin_width
