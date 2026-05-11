from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle


ROOT = Path(r"e:\sem8\ful\Diplom_NK\beck")
OUT_PDF = ROOT / "docs" / "architecture_layers_circles.pdf"
OUT_PNG = ROOT / "docs" / "architecture_layers_circles.png"

# Последняя согласованная таблица метрик:
# layer, out, in, NA, NC, I, A, D
METRICS = {
    "adapter": {"out": 1, "in": 0, "na": 0, "nc": 1, "i": 1.000, "a": 0.000, "d": 0.000},
    "controllers": {"out": 1, "in": 1, "na": 1, "nc": 2, "i": 0.500, "a": 0.500, "d": 0.000},
    "services": {"out": 0, "in": 13, "na": 15, "nc": 17, "i": 0.000, "a": 0.880, "d": 0.120},
    "repositories": {"out": 12, "in": 0, "na": 0, "nc": 1, "i": 1.000, "a": 0.000, "d": 0.000},
}


def _fmt_layer_text(layer: str) -> str:
    m = METRICS[layer]
    return (
        f"{layer}\n"
        f"I={m['i']:.3f}, A={m['a']:.3f}, D={m['d']:.3f}\n"
        f"out={m['out']}, in={m['in']}, NA={m['na']}, NC={m['nc']}"
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(9, 9), dpi=200)

    # Концентрические круги: внешний уровень общий для adapter и repositories.
    circles = [
        ("outer", 1.00, "#DCE9FF"),       # adapter + repositories (один уровень)
        ("controllers", 0.64, "#D9F2D9"),
        ("services", 0.34, "#FADBD8"),
    ]

    for layer, radius, color in circles:
        ax.add_patch(
            Circle(
                (0.0, 0.0),
                radius,
                facecolor=color,
                edgecolor="#333333",
                linewidth=1.8,
                alpha=0.95,
            )
        )

    # Подписи слоев.
    ax.text(0.0, 0.0, _fmt_layer_text("services"), ha="center", va="center", fontsize=10, weight="bold")
    ax.text(0.0, 0.49, _fmt_layer_text("controllers"), ha="center", va="center", fontsize=9)
    ax.text(-0.58, 0.78, _fmt_layer_text("adapter"), ha="center", va="center", fontsize=9)
    ax.text(0.58, 0.78, _fmt_layer_text("repositories"), ha="center", va="center", fontsize=9)

    ax.set_title("Слои архитектуры в виде концентрических кругов", fontsize=14, pad=16)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT_PDF, bbox_inches="tight")
    fig.savefig(OUT_PNG, bbox_inches="tight")
    print(str(OUT_PDF))
    print(str(OUT_PNG))


if __name__ == "__main__":
    main()
