"""
Максимально допустимое напряжение на рентгеновской трубке (кВ) из БД:
public.voltage_tube + type_metall по материалу и радиационной толщине.

Если материал или толщина не заданы, материал не найден в type_metall или нет
подходящих строк — считаем предел 0 кВ (см. IVoltageTubeDB / PostgresDataBase).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from repositories.Interfaces.i_voltage_tube_db import IVoltageTubeDB
from services.tech_card import TechCardData
from services.Changers.param_choice import is_scalar_choice
from services.Changers.ch_MaterialsFromDb import MaterialsFromDb

BLOCK_OBJECT = "Объект контроля"
BLOCK_SOURCE = "ИСХОДНЫЕ ДАННЫЕ"
PARAM_THICKNESS = "Номинальная толщина стенки, S, мм"
PARAM_RADIATION_THICKNESS = "Радиационная толщина, мм"


def format_table_kv_text(kv: float) -> str:
    """Строка для поля «Напряжение …, не более, кВ»."""
    if kv != kv:  # nan
        return "0"
    r = float(kv)
    if abs(r - round(r)) < 1e-9:
        return str(int(round(r)))
    t = f"{r:.6f}".rstrip("0").rstrip(".")
    return t if t else "0"


def _parse_thickness_mm(raw) -> Optional[float]:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    t = str(raw).strip().replace(",", ".")
    if not t:
        return None
    try:
        return float(t)
    except ValueError:
        m = re.search(r"[-+]?\d*\.?\d+", t)
        if not m:
            return None
        try:
            return float(m.group(0))
        except ValueError:
            return None


def _parse_apparatus_max_kv(raw) -> Optional[float]:
    """Максимальное напряжение трубки из поля БД аппарата (число или извлечение из строки)."""
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    text = str(raw).strip().replace(",", ".")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        nums = [float(m.group(0)) for m in re.finditer(r"[-+]?\d*\.?\d+", text)]
        return max(nums) if nums else None


def _read_thickness_mm_for_xray_table(data: TechCardData) -> Optional[float]:
    if data.has_block(BLOCK_OBJECT) and data.has_block_and_param(
        BLOCK_OBJECT, PARAM_THICKNESS
    ):
        t = _parse_thickness_mm(data.get_param_value(BLOCK_OBJECT, PARAM_THICKNESS))
        if t is not None:
            return t
    if data.has_block(BLOCK_SOURCE) and data.has_block_and_param(
        BLOCK_SOURCE, PARAM_RADIATION_THICKNESS
    ):
        t = _parse_thickness_mm(
            data.get_param_value(BLOCK_SOURCE, PARAM_RADIATION_THICKNESS)
        )
        if t is not None:
            return t
    return None


def read_material_and_thickness(
    data: TechCardData,
) -> Tuple[Optional[str], Optional[float]]:
    """Материал из ОТК / «ИСХОДНЫЕ ДАННЫЕ» (скаляр); толщина — см. _read_thickness_mm_for_xray_table."""
    material: Optional[str] = None
    for block_key in (MaterialsFromDb.BLOCK_NAME, MaterialsFromDb.LEGACY_BLOCK_NAME):
        if data.has_block_and_param(block_key, MaterialsFromDb.PARAM_NAME):
            v = data.get_param_value(block_key, MaterialsFromDb.PARAM_NAME)
            if is_scalar_choice(v):
                material = str(v).strip()
            break

    thickness_mm = _read_thickness_mm_for_xray_table(data)
    return material, thickness_mm


def max_permissible_kv_for_card(data: TechCardData, vt_db: IVoltageTubeDB) -> float:
    """Максимально допустимое кВ из БД; при нехватке данных — 0.0."""
    material, s_mm = read_material_and_thickness(data)
    if material is None or s_mm is None:
        return 0.0
    return vt_db.get_max_voltage_kv_for_material_and_thickness(material, s_mm)


def filter_rengen_apparatus_rows(
    rows: List[Dict[str, Any]],
    data: TechCardData,
    vt_db: IVoltageTubeDB,
) -> List[Dict[str, Any]]:
    """
    Предел из voltage_tube — максимально **допустимое** напряжение на трубке, кВ.
    Аппарат подходит, если заявленное им максимальное напряжение **не выше** этого предела
    (строго выше — не подходит). Записи с неразборчивым напряжением оставляем.
    """
    limit_kv = max_permissible_kv_for_card(data, vt_db)
    out: List[Dict[str, Any]] = []
    for row in rows:
        v = _parse_apparatus_max_kv(row.get("voltage_on_tube"))
        if v is None:
            out.append(row)
        elif v <= limit_kv:
            out.append(row)
    return out
