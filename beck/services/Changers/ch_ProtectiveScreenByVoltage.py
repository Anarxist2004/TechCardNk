import re
from typing import Optional

from services.Interfaces.i_dataChanger import IDataChanger
from services.tech_card import TechCardData


SOURCE_BLOCK = "ИСХОДНЫЕ ДАННЫЕ"
VOLTAGE_PARAM_NAMES = (
    "Напряжение на рентгеновской трубке, не более, кВ",
    "Напряжение на рентгеновской  трубке, не более, кВ",
)
TARGET_PARAM = "Толщина защитного экрана, мм"


def _get_existing_param_value(data: TechCardData, block_name: str, param_names):
    names = (param_names,) if isinstance(param_names, str) else tuple(param_names)
    for name in names:
        if data.has_block_and_param(block_name, name):
            return data.get_param_value(block_name, name)
    return None


def _parse_voltage_kv(value) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (list, tuple, dict)):
        return None
    text = str(value).strip().replace(",", ".")
    if not text:
        return None
    try:
        return float(text)
    except (TypeError, ValueError):
        match = re.search(r"[-+]?\d*\.?\d+", text)
        if not match:
            return None
        try:
            return float(match.group(0))
        except (TypeError, ValueError):
            return None


def _resolve_protective_screen_thickness(voltage_kv: float) -> str:
    # Используем только строки для рентген-аппаратов из таблицы:
    # - до 200 кВ -> До 1,0
    # - свыше 200 кВ -> От 1,0 до 2,0
    if voltage_kv <= 200:
        return "До 1,0"
    return "От 1,0 до 2,0"


class ProtectiveScreenByVoltage(IDataChanger[TechCardData]):
    """
    Поддерживает актуальное значение поля
    «Толщина защитного экрана, мм»
    только для рентген-аппаратов (по напряжению трубки).
    """

    def changeData(self, data: TechCardData) -> TechCardData:
        if not data.has_block_and_param(SOURCE_BLOCK, TARGET_PARAM):
            return data

        voltage_raw = _get_existing_param_value(data, SOURCE_BLOCK, VOLTAGE_PARAM_NAMES)
        voltage_kv = _parse_voltage_kv(voltage_raw)
        if voltage_kv is None:
            data.set_param_value(SOURCE_BLOCK, TARGET_PARAM, None)
            return data

        expected = _resolve_protective_screen_thickness(voltage_kv)
        current = data.get_param_value(SOURCE_BLOCK, TARGET_PARAM)
        if isinstance(current, str) and current.strip() == expected:
            return data

        data.set_param_value(SOURCE_BLOCK, TARGET_PARAM, expected)
        return data

