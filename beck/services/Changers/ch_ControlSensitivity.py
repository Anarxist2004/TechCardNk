from services.Interfaces.i_dataChanger import IDataChanger
from services.tech_card import TechCardData


QUALITY_PARAM = "Уровень качества"
THICKNESS_PARAM = "Радиационная толщина, мм"
TARGET_PARAM_NAMES = (
    "Чувствительность контроля, мм",
    "Чувствительность контроля",
)

QUALITY_TO_CLASS = {
    "A": 2,
    "B": 1,
    "C": 3,
}

SENSITIVITY_TABLE = [
    (5.0, {1: "0,10", 2: "0,10", 3: "0,20"}),
    (9.0, {1: "0,20", 2: "0,20", 3: "0,30"}),
    (12.0, {1: "0,20", 2: "0,30", 3: "0,40"}),
    (20.0, {1: "0,30", 2: "0,40", 3: "0,50"}),
    (30.0, {1: "0,40", 2: "0,50", 3: "0,60"}),
    (40.0, {1: "0,50", 2: "0,60", 3: "0,75"}),
    (50.0, {1: "0,60", 2: "0,75", 3: "1,00"}),
    (70.0, {1: "0,75", 2: "1,00", 3: "1,25"}),
    (100.0, {1: "1,00", 2: "1,25", 3: "1,50"}),
    (140.0, {1: "1,25", 2: "1,50", 3: "2,00"}),
    (200.0, {1: "1,50", 2: "2,00", 3: "2,50"}),
    (300.0, {1: "2,00", 2: "2,50"}),
    (400.0, {1: "2,50"}),
]


def _iter_param_locations(data: TechCardData, param_names) -> list[tuple[str, str]]:
    if isinstance(param_names, str):
        names = {param_names}
    else:
        names = set(param_names)

    locations: list[tuple[str, str]] = []
    for block in data.params.values():
        block_name = block.get("name")
        if not block_name:
            continue
        for param in block.get("params", {}).values():
            param_name = param.get("name")
            if param_name in names:
                locations.append((block_name, param_name))
    return locations


def _get_first_param_value(data: TechCardData, param_name: str):
    locations = _iter_param_locations(data, param_name)
    if not locations:
        return None
    block_name, found_param_name = locations[0]
    return data.get_param_value(block_name, found_param_name)


def _parse_quality_class(value) -> int | None:
    if value is None or isinstance(value, (list, tuple)):
        return None

    quality = str(value).strip().upper()
    if not quality:
        return None

    return QUALITY_TO_CLASS.get(quality)


def _parse_thickness_mm(value) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (list, tuple)):
        return None
    if isinstance(value, (int, float)):
        return float(value)

    raw = str(value).strip().replace(",", ".")
    if not raw:
        return None

    try:
        return float(raw)
    except ValueError:
        return None


def _lookup_sensitivity(control_class: int | None, thickness_mm: float | None) -> str | None:
    if control_class is None or thickness_mm is None:
        return None
    if thickness_mm < 0:
        return None

    for max_thickness, values_by_class in SENSITIVITY_TABLE:
        if thickness_mm <= max_thickness:
            return values_by_class.get(control_class)
    return None


class ControlSensitivityChanger(IDataChanger[TechCardData]):
    """
    Автоматически рассчитывает «Чувствительность контроля» по уровню качества
    и радиационной толщине.
    """

    def changeData(self, data: TechCardData) -> TechCardData:
        quality_value = _get_first_param_value(data, QUALITY_PARAM)
        thickness_value = _get_first_param_value(data, THICKNESS_PARAM)

        control_class = _parse_quality_class(quality_value)
        thickness_mm = _parse_thickness_mm(thickness_value)
        sensitivity_value = _lookup_sensitivity(control_class, thickness_mm)

        for block_name, param_name in _iter_param_locations(data, TARGET_PARAM_NAMES):
            data.set_param_value(block_name, param_name, sensitivity_value)

        return data
