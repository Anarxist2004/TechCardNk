from decimal import Decimal, InvalidOperation

from repositories.Interfaces.i_material_standard_db import IMaterialStandardDB
from services.Interfaces.i_dataChanger import IDataChanger
from services.Changers.param_choice import is_scalar_choice
from services.tech_card import TechCardData


TOP_BLOCK = (
    "ОПЕРАЦИОННАЯ ТЕХНОЛОГИЧЕСКАЯ КАРТА РАДИОГРАФИЧЕСКОГО КОНТРОЛЯ "
    "СВАРНЫХ СОЕДИНЕНИЙ"
)
SOURCE_BLOCK = "ИСХОДНЫЕ ДАННЫЕ"
MATERIAL_PARAM = "Материал"
SENSITIVITY_PARAM_NAMES = (
    "Чувствительность контроля, мм",
    "Чувствительность контроля",
)
TARGET_PARAM = "Тип и номер эталона чувствительности"

WIRE_ETALON_TABLE = [
    (
        1,
        {
            1: Decimal("0.20"),
            2: Decimal("0.16"),
            3: Decimal("0.125"),
            4: Decimal("0.10"),
            5: Decimal("0.08"),
            6: Decimal("0.063"),
            7: Decimal("0.05"),
        },
    ),
    (
        2,
        {
            1: Decimal("0.40"),
            2: Decimal("0.32"),
            3: Decimal("0.25"),
            4: Decimal("0.20"),
            5: Decimal("0.16"),
            6: Decimal("0.125"),
            7: Decimal("0.10"),
        },
    ),
    (
        3,
        {
            1: Decimal("1.25"),
            2: Decimal("1.00"),
            3: Decimal("0.80"),
            4: Decimal("0.63"),
            5: Decimal("0.50"),
            6: Decimal("0.40"),
            7: Decimal("0.32"),
        },
    ),
    (
        4,
        {
            1: Decimal("4.0"),
            2: Decimal("3.20"),
            3: Decimal("2.50"),
            4: Decimal("2.00"),
            5: Decimal("1.60"),
            6: Decimal("1.25"),
            7: Decimal("1.00"),
        },
    ),
]


def _wire_tolerance(value: Decimal) -> Decimal:
    if value <= Decimal("0.2"):
        return Decimal("0.01")
    if value <= Decimal("1.6"):
        return Decimal("0.03")
    return Decimal("0.04")


def _get_param_value(data: TechCardData, block_name: str, param_names):
    names = (param_names,) if isinstance(param_names, str) else tuple(param_names)
    if not data.has_block(block_name):
        return None

    for name in names:
        if data.has_block_and_param(block_name, name):
            return data.get_param_value(block_name, name)
    return None


def _parse_sensitivity_value(value) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (list, tuple)):
        return None
    if isinstance(value, Decimal):
        return value

    raw = str(value).strip().replace(",", ".")
    if not raw:
        return None

    try:
        return Decimal(raw)
    except (InvalidOperation, ValueError):
        return None


def _resolve_etalon_number(
    material_standard_id: int | None, sensitivity_value: Decimal | None
) -> int | None:
    if material_standard_id is None or sensitivity_value is None:
        return None
    if material_standard_id not in range(1, 8):
        return None

    for etalon_number, values_by_standard in WIRE_ETALON_TABLE:
        nominal_value = values_by_standard.get(material_standard_id)
        if nominal_value is None:
            continue
        tolerance = _wire_tolerance(nominal_value)
        if sensitivity_value <= nominal_value + tolerance:
            return etalon_number
    return None


class SensitivityEtalonByMaterial(IDataChanger[TechCardData]):
    """
    По выбранному материалу и значению «Чувствительность контроля»
    заполняет поле «Тип и номер эталона чувствительности» в формате
    «<id_standard><номер эталона> провол.», учитывая допуски по диаметрам
    проволочных эталонов из п. 2.10.
    """

    def __init__(self, db: IMaterialStandardDB):
        self._db = db

    def changeData(self, data: TechCardData) -> TechCardData:
        material_value = _get_param_value(data, TOP_BLOCK, MATERIAL_PARAM)
        sensitivity_raw = _get_param_value(
            data, SOURCE_BLOCK, SENSITIVITY_PARAM_NAMES
        )

        target_value = None
        if is_scalar_choice(material_value):
            material_standard_id = self._db.get_material_standard_id(
                str(material_value).strip()
            )
            sensitivity_value = _parse_sensitivity_value(sensitivity_raw)
            etalon_number = _resolve_etalon_number(
                material_standard_id, sensitivity_value
            )
            if material_standard_id is not None and etalon_number is not None:
                target_value = f"{material_standard_id}{etalon_number} провол."

        if data.has_block_and_param(SOURCE_BLOCK, TARGET_PARAM):
            data.set_param_value(SOURCE_BLOCK, TARGET_PARAM, target_value)
        elif target_value is not None:
            data.insert_param_to_block(
                SOURCE_BLOCK,
                5,
                {"name": TARGET_PARAM, "val": target_value},
            )
        return data
