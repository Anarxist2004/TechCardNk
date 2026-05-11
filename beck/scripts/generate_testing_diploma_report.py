"""
Генерация Word-отчёта по автоматическому тестированию (для дипломной работы).

Перед сборкой документа выполняется pytest; вывод включается в приложение.

Запуск из корня beck: python scripts/generate_testing_diploma_report.py
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.text import WD_LINE_SPACING
from docx.shared import Pt


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "testing_diploma_report.docx"
TESTS_DIR = ROOT / "tests"


def _set_body_style(doc: Document) -> None:
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    pf = style.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(6)


def _p(doc: Document, text: str) -> None:
    doc.add_paragraph(text)


def _heading(doc: Document, text: str, level: int) -> None:
    doc.add_heading(text, level=level)


def _run_pytest() -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(TESTS_DIR), "-v", "--tb=no"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return proc.returncode, out.strip()


def build_document(pytest_exit_code: int, pytest_log: str) -> Document:
    doc = Document()
    _set_body_style(doc)

    doc.add_heading(
        "Отчёт по автоматизированному тестированию компонентов серверной части приложения",
        0,
    )
    _p(
        doc,
        f"Документ подготовлен для дипломной работы по проекту формирования операционной "
        f"технологической карты радиографического контроля. Дата формирования отчёта: "
        f"{datetime.now().strftime('%d.%m.%Y %H:%M')}. Корень исходного кода: каталог "
        f"`beck`; тесты расположены в подкаталоге `tests/`.",
    )

    _heading(doc, "1. Цели и задачи тестирования в рамках проекта", 1)
    _p(
        doc,
        "Автоматизированное тестирование в программной инженерии служит нескольким "
        "связанным целям. Во-первых, оно позволяет регрессионно контролировать поведение "
        "системы после изменений в коде: исправление ошибки или добавление функции не "
        "должно незаметно нарушать уже работавшие сценарии. Во-вторых, модульные и "
        "интеграционные тесты документируют ожидаемое поведение компонентов в исполняемой "
        "форме, что особенно полезно при передаче проекта или работе в составе команды. "
        "В-третьих, тесты с подставными объектами (mock, stub) уменьшают зависимость "
        "проверок от внешних систем — в частности, от экземпляра СУБД PostgreSQL, что "
        "упрощает воспроизводимый запуск на рабочей станции разработчика или в среде CI.",
    )
    _p(
        doc,
        "В контексте дипломного проекта задачей набора тестов является не исчерпывающее "
        "покрытие всего кода процентными метриками, а демонстрация освоения практики "
        "построения проверяемой архитектуры: выделение слоёв, использование интерфейсов "
        "(`IRepository`, `IServise`, `IControllers`, `IDataChanger`), проверка ключевых "
        "структур данных (`TechCardData`, `PipeLine`) и фрагмента предметной логики без "
        "подключения к базе данных.",
    )

    _heading(doc, "2. Выбранные средства и конфигурация", 1)
    _p(
        doc,
        "В качестве фреймворка тестирования используется **pytest** — распространённое "
        "решение для языка Python, поддерживающее лаконичный синтаксис тестовых функций, "
        "параметризацию, фикстуры и подробные отчёты об ошибках. Зависимость зафиксирована "
        "в файле `requirements-dev.txt` в корне проекта; установка выполняется командой "
        "`python -m pip install -r requirements-dev.txt`.",
    )
    _p(
        doc,
        "В файле `pytest.ini` заданы параметры `pythonpath = .` (импорты пакетов `services`, "
        "`repositories`, `controllers` относительно корня `beck`) и `testpaths = tests`, "
        "чтобы при запуске из корня проекта обнаруживались только тесты из выделенного "
        "каталога.",
    )

    _heading(doc, "3. Структура каталога tests", 1)
    rows = [
        ("`tests/conftest.py`", "Общие фикстуры: класс `NoOpChanger` (пустой IDataChanger) и фикстура `pipeline_noop`."),
        ("`tests/test_pipeline.py`", "Поведение `PipeLine`: ошибки индексов, порядок вызова changer’ов, сортировка параметров."),
        ("`tests/test_tech_card_data.py`", "Сериализация JSON, десериализация, поиск блоков и параметров, вставка и дубликаты."),
        ("`tests/test_tech_card_service.py`", "`TechCardService` с `MagicMock(spec=IRepository)`: шаблон, сохранение, операции из БД."),
        ("`tests/test_controller_web.py`", "`ControllerWeb` с подставным `IServise`: шаблон, обновление, делегирование."),
        ("`tests/test_circ_butt_weld_changer.py`", "Табличная логика `CircButtWeldBeadFromThicknessTable` и вспомогательные функции."),
    ]
    for path, desc in rows:
        _p(doc, f"{path} — {desc}")

    _heading(doc, "4. Классификация тестов по уровням", 1)
    _p(
        doc,
        "**Модульные тесты** проверяют отдельные классы и функции в изоляции: например, "
        "разбор строки толщины `_parse_s_mm`, выбор строки таблицы `_lookup_e_g`, правила "
        "`PipeLine` при пустом или заполненном списке преобразователей. **Тесты с "
        "двойниками зависимостей** используют `unittest.mock.MagicMock` с ограничением "
        "`spec=` по интерфейсу репозитория или сервиса: так проверяется, что сервис "
        "корректно вызывает методы сохранения и загрузки, не требуя реальной PostgreSQL. "
        "**Сквозные HTTP-тесты** FastAPI в данный набор намеренно не включались, чтобы "
        "не запускать сервер и не дублировать логику маршрутизации `adapterWeb.py` в "
        "отчёте; при необходимости их можно добавить через `httpx.AsyncClient` и "
        "`TestClient`.",
    )

    _heading(doc, "5. Запуск тестов", 1)
    _p(
        doc,
        "Из каталога `beck` выполните: `python -m pytest tests -v`. Краткий отчёт без "
        "трассировок: `python -m pytest tests -q`.",
    )

    _heading(doc, "6. Результат контрольного прогона при сборке отчёта", 1)
    status = "успешно (код завершения 0)" if pytest_exit_code == 0 else f"код завершения {pytest_exit_code}"
    _p(doc, f"Прогон pytest при генерации данного документа завершился {status}.")
    _p(doc, "Ниже приведён сокращённый вывод команды `pytest -v --tb=no`:")
    for line in pytest_log.splitlines():
        doc.add_paragraph(line, style="Normal")

    _heading(doc, "7. Выводы", 1)
    _p(
        doc,
        "Созданный набор тестов покрывает критичные участки серверной логики: конвейер "
        "обработки техкарты, модель данных, сервис с подстановкой репозитория, контроллер "
        "с подстановкой сервиса, а также предметный changer на табличных данных. Такое "
        "распределение соответствует рекомендациям по тестированию многослойных приложений "
        "и может служить основой для расширения покрытия (репозиторий PostgreSQL на "
        "тестовой БД, HTTP-слой, дополнительные changer’ы).",
    )

    return doc


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    code, log = _run_pytest()
    doc = build_document(code, log)
    doc.save(OUTPUT)
    print(f"Written: {OUTPUT} (pytest exit code={code})")
    if code != 0:
        sys.exit(code)


if __name__ == "__main__":
    main()
