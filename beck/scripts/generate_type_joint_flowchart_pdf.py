from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon


OUT_PDF = Path(r"e:\sem8\ful\Diplom_NK\beck\docs\type_of_welded_joint_flowchart.pdf")


def add_rect(ax, xy, w, h, text, rounded=False, fs=9):
    boxstyle = "round,pad=0.02,rounding_size=0.02" if rounded else "square,pad=0.02"
    p = FancyBboxPatch(
        xy,
        w,
        h,
        boxstyle=boxstyle,
        edgecolor="black",
        facecolor="white",
        linewidth=1.2,
    )
    ax.add_patch(p)
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center", fontsize=fs)


def add_parallelogram(ax, xy, w, h, text, fs=8.5, skew=0.035):
    x, y = xy
    pts = [(x + skew, y), (x + w, y), (x + w - skew, y + h), (x, y + h)]
    p = Polygon(pts, closed=True, edgecolor="black", facecolor="white", linewidth=1.2)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def add_diamond(ax, center, w, h, text, fs=9):
    cx, cy = center
    pts = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
    p = Polygon(pts, closed=True, edgecolor="black", facecolor="white", linewidth=1.2)
    ax.add_patch(p)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs)


def arrow(ax, x1, y1, x2, y2, txt=None, tx=None, ty=None):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color="black", lw=1.1),
    )
    if txt is not None:
        ax.text(tx if tx is not None else (x1 + x2) / 2, ty if ty is not None else (y1 + y2) / 2, txt, fontsize=8)


def main() -> None:
    fig, ax = plt.subplots(figsize=(8.27, 11.69), dpi=200)  # A4 portrait
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.5, 0.975, "Блок-схема: TypeOfWeldedJointFromDb", ha="center", va="top", fontsize=12, fontweight="bold")

    # Nodes
    add_rect(ax, (0.42, 0.91), 0.16, 0.04, "Старт", rounded=True)

    add_parallelogram(
        ax,
        (0.16, 0.80),
        0.68,
        0.085,
        "Вход:\n- Одиночный выбор «НОРМАТИВНЫЕ ДОКУМЕНТЫ»\n- Наличие блока «Объект контроля»\n- Текущее состояние поля «Тип сварного соединения»",
        fs=8.4,
    )

    add_rect(
        ax,
        (0.20, 0.71),
        0.60,
        0.055,
        "Проверка блоков и наличия исходного параметра в верхнем блоке",
        fs=8.8,
    )

    add_diamond(ax, (0.50, 0.62), 0.42, 0.11, "«Тип сварного соединения»\nуже непустой?", fs=9)

    add_rect(ax, (0.74, 0.55), 0.20, 0.05, "Не изменять значение", fs=8.8)
    add_rect(ax, (0.18, 0.52), 0.64, 0.055, "Чтение БД по id/названию нормативного документа", fs=8.8)
    add_rect(ax, (0.22, 0.44), 0.56, 0.05, "Формирование списка допустимых типов шва", fs=8.8)
    add_rect(
        ax,
        (0.15, 0.35),
        0.70,
        0.07,
        "Запись списка в параметр «Тип сварного соединения»\nи установка subtitle «ОБЪЕКТ КОНТРОЛЯ»",
        fs=8.6,
    )

    add_parallelogram(
        ax,
        (0.18, 0.24),
        0.64,
        0.075,
        "Выход:\n- Поле «Тип сварного соединения» обновлено списком допустимых типов шва\n- Установлен subtitle «ОБЪЕКТ КОНТРОЛЯ»",
        fs=8.2,
    )

    add_rect(ax, (0.42, 0.16), 0.16, 0.04, "Завершение", rounded=True)

    # Arrows
    arrow(ax, 0.50, 0.91, 0.50, 0.885)
    arrow(ax, 0.50, 0.80, 0.50, 0.765)
    arrow(ax, 0.50, 0.71, 0.50, 0.675)

    # Decision branches
    arrow(ax, 0.71, 0.62, 0.74, 0.575, "Да", 0.715, 0.635)
    arrow(ax, 0.84, 0.55, 0.58, 0.20)
    arrow(ax, 0.58, 0.20, 0.58, 0.18)

    arrow(ax, 0.50, 0.565, 0.50, 0.575, "Нет", 0.515, 0.57)
    arrow(ax, 0.50, 0.52, 0.50, 0.49)
    arrow(ax, 0.50, 0.44, 0.50, 0.42)
    arrow(ax, 0.50, 0.35, 0.50, 0.315)
    arrow(ax, 0.50, 0.24, 0.50, 0.20)

    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PDF, format="pdf", bbox_inches="tight")
    print(str(OUT_PDF))


if __name__ == "__main__":
    main()
