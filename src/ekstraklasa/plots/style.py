from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ekstraklasa.config import FIG_DIR


def save_figure(fig: plt.Figure, filename: str, *, output_dir: Path | None = None, dpi: int = 150, **savefig_kwargs) -> Path:
    out_path = (output_dir or FIG_DIR) / filename
    fig.savefig(out_path, dpi=dpi, **savefig_kwargs)
    plt.close(fig)
    print(f"  saved {out_path}")
    return out_path


def clean_axes(ax) -> None:
    """Remove top/right spines and put grid behind data."""
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
