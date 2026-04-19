"""
Таблица S → (e, g) по номинальной толщине стенки:

- «Стыковое кольцевое. Автоматическая, односторонняя»: e → A, g → h1=h2;
- «Листовое сварное соединение»: e → «e, не более», g → «g».
"""

from __future__ import annotations

from typing import Optional, Tuple

from services.Interfaces.i_dataChanger import IDataChanger
from services.tech_card import TechCardData
from services.Changers.param_choice import is_scalar_choice


JOINT_TYPE_CIRC = "Стыковое кольцевое. Автоматическая, односторонняя"
JOINT_TYPE_SHEET = "Листовое сварное соединение"

BLOCK_OBJECT = "Объект контроля"
PARAM_JOINT = "Тип сварного соединения"
PARAM_THICKNESS = "Номинальная толщина стенки, S, мм"

_PARAM_BEAD_WIDTH_A_ALIASES = (
    "Ширина верхнего валика, А, мм",
    "Ширина верхнего валика, A, мм",
)
PARAM_BEAD_H1 = "Высота верхнего валика, h1, мм"
PARAM_BEAD_H2 = "Высота нижнего валика, h2, мм"

PARAM_SHEET_E = "e, не более"
PARAM_SHEET_G = "g"

# Диапазоны S [мм] включительно: (s_min, s_max, e_mm, g_mm)
_EG_BY_THICKNESS_MM: Tuple[Tuple[float, float, float, float], ...] = (
    (2, 2, 7, 1.5),
    (3, 4, 8, 1.5),
    (5, 5, 10, 1.5),
    (6, 8, 13, 1.5),
    (9, 10, 15, 1.5),
    (12, 12, 18, 1.5),
    (14, 14, 22, 1.5),
    (16, 16, 24, 2.0),
    (18, 18, 26, 2.0),
    (20, 20, 29, 2.0),
    (25, 30, 39, 2.0),
    (35, 40, 50, 2.0),
)


def _parse_s_mm(raw) -> Optional[float]:
    if raw is None:
        return None
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    s = str(raw).strip().replace(",", ".")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _lookup_e_g(s_mm: float) -> Optional[Tuple[float, float]]:
    for lo, hi, e_mm, g_mm in _EG_BY_THICKNESS_MM:
        if lo <= s_mm <= hi:
            return (e_mm, g_mm)
    return None


def _fmt_mm(v: float) -> str:
    r = round(float(v), 6)
    if abs(r - round(r)) < 1e-9:
        return str(int(round(r)))
    t = f"{r:.6f}".rstrip("0").rstrip(".")
    return t if t else "0"


class CircButtWeldBeadFromThicknessTable(IDataChanger[TechCardData]):
    """
    По числовой «Номинальная толщина стенки, S, мм» и типу шва подставляет
    значения из одной и той же таблицы (e, g): для стыкового кольцевого — A, h1, h2;
    для листового — «e, не более» и «g». Вне диапазонов таблицы поля не меняет.
    """

    def changeData(self, data: TechCardData) -> TechCardData:
        if not data.has_block(BLOCK_OBJECT):
            return data
        if not data.has_block_and_param(BLOCK_OBJECT, PARAM_JOINT):
            return data

        joint_val = data.get_param_value(BLOCK_OBJECT, PARAM_JOINT)
        if not is_scalar_choice(joint_val):
            return data
        joint = str(joint_val).strip()

        if joint == JOINT_TYPE_CIRC:
            return self._apply_circ_butt(data)
        if joint == JOINT_TYPE_SHEET:
            return self._apply_sheet(data)
        return data

    def _read_s_mm(self, data: TechCardData) -> Optional[float]:
        if not data.has_block_and_param(BLOCK_OBJECT, PARAM_THICKNESS):
            return None
        return _parse_s_mm(data.get_param_value(BLOCK_OBJECT, PARAM_THICKNESS))

    def _apply_circ_butt(self, data: TechCardData) -> TechCardData:
        s_mm = self._read_s_mm(data)
        if s_mm is None:
            return data
        pair = _lookup_e_g(s_mm)
        if pair is None:
            return data
        e_mm, g_mm = pair
        a_text = _fmt_mm(e_mm)
        g_text = _fmt_mm(g_mm)

        pname_a = next(
            (n for n in _PARAM_BEAD_WIDTH_A_ALIASES if data.has_block_and_param(BLOCK_OBJECT, n)),
            None,
        )
        if pname_a is None:
            return data
        for pname in (PARAM_BEAD_H1, PARAM_BEAD_H2):
            if not data.has_block_and_param(BLOCK_OBJECT, pname):
                return data

        data.set_param_value(BLOCK_OBJECT, pname_a, a_text)
        data.set_param_value(BLOCK_OBJECT, PARAM_BEAD_H1, g_text)
        data.set_param_value(BLOCK_OBJECT, PARAM_BEAD_H2, g_text)
        return data

    def _apply_sheet(self, data: TechCardData) -> TechCardData:
        s_mm = self._read_s_mm(data)
        if s_mm is None:
            return data
        pair = _lookup_e_g(s_mm)
        if pair is None:
            return data
        e_mm, g_mm = pair
        e_text = _fmt_mm(e_mm)
        g_text = _fmt_mm(g_mm)

        if not data.has_block_and_param(BLOCK_OBJECT, PARAM_SHEET_E):
            return data
        if not data.has_block_and_param(BLOCK_OBJECT, PARAM_SHEET_G):
            return data

        data.set_param_value(BLOCK_OBJECT, PARAM_SHEET_E, e_text)
        data.set_param_value(BLOCK_OBJECT, PARAM_SHEET_G, g_text)
        return data
