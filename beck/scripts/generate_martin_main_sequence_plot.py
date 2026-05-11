from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

# Данные слоёв (скорректированная таблица для диплома): out, in, NA, NC, I, A, D
LAYERS_TABLE: list[tuple[str, int, int, int, int, float, float, float]] = [
    ("adapter", 1, 0, 0, 1, 1.000, 0.0, 0.0),
    ("controllers", 1, 1, 1, 2, 0.500, 0.5, 0.0),
    ("services", 0, 13, 15, 17, 0.000, 0.88, 0.12),
    ("repositories", 12, 0, 0, 1, 1.000, 0.0, 0.0),
]

OUT_PNG = Path(__file__).resolve().parents[1] / "docs" / "martin_main_sequence.png"
OUT_SVG = Path(__file__).resolve().parents[1] / "docs" / "martin_main_sequence.svg"
OUT_PDF = Path(__file__).resolve().parents[1] / "docs" / "martin_main_sequence.pdf"


def main() -> None:
    fig, ax = plt.subplots(figsize=(7, 7), dpi=180)

    ax.plot([0, 1], [1, 0], linestyle="--", linewidth=1.8, color="gray", label="I = 1 − A")

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    # Подписи для совпадающих точек (A=0, I=1): adapter и repositories
    overlap_offsets = {
        "adapter": (8, 8),
        "repositories": (8, -12),
    }

    for idx, row in enumerate(LAYERS_TABLE):
        name, _out, _inn, _na, _nc, i_val, a_val, _d = row
        c = colors[idx % len(colors)]
        ax.scatter([a_val], [i_val], s=85, c=c, edgecolors="black", linewidths=0.6, zorder=3)
        off = overlap_offsets.get(name, (6, 6))
        ax.annotate(
            name,
            (a_val, i_val),
            textcoords="offset points",
            xytext=off,
            fontsize=9,
        )


    ax.set_xlabel("A (Abstractness)")
    ax.set_ylabel("I (Instability)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.35)
    ax.legend(loc="lower left", fontsize=8)

    fig.tight_layout()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, bbox_inches="tight")
    fig.savefig(OUT_SVG, bbox_inches="tight")
    fig.savefig(OUT_PDF, bbox_inches="tight")
    print(str(OUT_PNG))
    print(str(OUT_SVG))
    print(str(OUT_PDF))


if __name__ == "__main__":
    main()
