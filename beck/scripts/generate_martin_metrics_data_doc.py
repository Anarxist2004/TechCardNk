from __future__ import annotations

from datetime import datetime
from pathlib import Path

from docx import Document
from docx.shared import Pt


ROOT = Path(r"e:\sem8\ful\Diplom_NK\beck")
OUTPUT = ROOT / "docs" / "martin_metrics_updated_description.docx"

# Входные данные пользователя: out, in, NA, NC, I, A, D
ROWS = [
    {
        "layer": "adapter",
        "out": 1,
        "inn": 0,
        "na": 0,
        "nc": 1,
        "i": 1.000,
        "a": 0.000,
        "d": 0.000,
    },
    {
        "layer": "controllers",
        "out": 1,
        "inn": 1,
        "na": 1,
        "nc": 2,
        "i": 0.500,
        "a": 0.500,
        "d": 0.000,
    },
    {
        "layer": "services",
        "out": 0,
        "inn": 13,
        "na": 15,
        "nc": 17,
        "i": 0.000,
        "a": 0.880,
        "d": 0.120,
    },
    {
        "layer": "repositories",
        "out": 12,
        "inn": 0,
        "na": 0,
        "nc": 1,
        "i": 1.000,
        "a": 0.000,
        "d": 0.000,
    },
]


def fmt(x: float) -> str:
    return f"{x:.3f}"


def add_intro(doc: Document) -> None:
    doc.add_heading("Описание скорректированных метрик архитектуры", 0)
    doc.add_paragraph(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    doc.add_paragraph(
        "Документ описывает предоставленные значения метрик для слоев "
        "adapter, controllers, services, repositories. Используются показатели "
        "внешних и входящих зависимостей (out/in), количества абстракций (NA), "
        "общего числа классов (NC), а также метрики Роберта Мартина: I, A и D."
    )


def add_formula_block(doc: Document) -> None:
    doc.add_heading("1. Что означают метрики", level=1)
    for line in (
        "I (Instability) = out / (out + in): чем выше I, тем более «изменчив» слой.",
        "A (Abstractness) = NA / NC: доля абстрактных классов в слое.",
        "D = |A + I - 1|: расстояние до Main Sequence (чем ближе к 0, тем лучше баланс).",
    ):
        doc.add_paragraph(line, style="List Bullet")


def add_source_table(doc: Document) -> None:
    doc.add_heading("2. Входные данные", level=1)
    table = doc.add_table(rows=1, cols=8)
    hdr = table.rows[0].cells
    hdr[0].text = "Layer"
    hdr[1].text = "out"
    hdr[2].text = "in"
    hdr[3].text = "NA"
    hdr[4].text = "NC"
    hdr[5].text = "I"
    hdr[6].text = "A"
    hdr[7].text = "D"

    for row in ROWS:
        cells = table.add_row().cells
        cells[0].text = row["layer"]
        cells[1].text = str(row["out"])
        cells[2].text = str(row["inn"])
        cells[3].text = str(row["na"])
        cells[4].text = str(row["nc"])
        cells[5].text = fmt(row["i"])
        cells[6].text = fmt(row["a"])
        cells[7].text = fmt(row["d"])


def add_layer_interpretation(doc: Document) -> None:
    doc.add_heading("3. Интерпретация по слоям", level=1)
    doc.add_paragraph(
        "adapter: I=1.000 и A=0.000 при D=0.000. Слой полностью нестабилен "
        "(исходит наружу, входящих связей нет), но находится на Main Sequence."
    )
    doc.add_paragraph(
        "controllers: I=0.500 и A=0.500, D=0.000. Наиболее сбалансированная точка: "
        "равновесие между зависимостями и абстракциями."
    )
    doc.add_paragraph(
        "services: I=0.000 и A=0.880, D=0.120. Слой очень стабильный и при этом "
        "высоко абстрактный. Отклонение от Main Sequence умеренное, но приемлемое."
    )
    doc.add_paragraph(
        "repositories: I=1.000, A=0.000, D=0.000. Метрика указывает на полностью "
        "нестабильный слой без абстракций, формально на Main Sequence."
    )


def add_conclusion(doc: Document) -> None:
    avg_d = sum(row["d"] for row in ROWS) / len(ROWS)
    doc.add_heading("4. Общий вывод", level=1)
    doc.add_paragraph(
        "Среднее расстояние до Main Sequence по четырем слоям составляет "
        f"{fmt(avg_d)}. Это указывает на в целом хорошую сбалансированность архитектуры "
        "по выбранным данным."
    )
    doc.add_paragraph(
        "Рекомендуется в следующей итерации дополнительно проверить направленность "
        "межслойных зависимостей и наличие циклов, чтобы подтвердить качество не только "
        "по геометрии точки (A, I), но и по структуре графа зависимостей."
    )


def main() -> None:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)

    add_intro(doc)
    add_formula_block(doc)
    add_source_table(doc)
    add_layer_interpretation(doc)
    add_conclusion(doc)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    print(str(OUTPUT))


if __name__ == "__main__":
    main()
