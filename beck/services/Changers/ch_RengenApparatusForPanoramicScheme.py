import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from repositories.Interfaces.i_rengen_apparatus_db import IRengenApparatusDB
from services.Changers.param_choice import is_scalar_choice
from services.Interfaces.i_dataChanger import IDataChanger
from services.tech_card import TechCardData


BLOCK_SOURCE = "ИСХОДНЫЕ ДАННЫЕ"
PARAM_SCHEME = "схема просвечивания"
TARGET_SCHEME = "Панорамное просвечивание кольцевого сварного соединения"
PARAM_APPARATUS = "ИИИ"
LEGACY_PARAM_APPARATUS = "ИИИ Рентгеновский аппарат"
PARAM_FOCAL_SPOT = "Размер фокусного пятна ИИИ, мм"
PARAM_VOLTAGE = "Напряжение на рентгеновской трубке, не более, кВ"
ALT_PARAM_VOLTAGE = "Напряжение на рентгеновской  трубке, не более, кВ"
PARAM_DISTANCE_NAMES = (
    "Расстояние от ИИИ до поверхности контролируемого сварного соединения, мм",
    "Расстояние от ИИИ до поверхности  контролируемого сварного соединения, мм",
)
PARAM_NOMINAL_DIAMETER = "Номинальный диаметр трубы, мм"
PARAM_WALL_THICKNESS = "Номинальная толщина стенки, S, мм"
SENSITIVITY_PARAM_NAMES = (
    "Чувствительность контроля, мм",
    "Чувствительность контроля",
)
_TARGET_SCHEME_KEY = re.sub(r"\s+", " ", TARGET_SCHEME).strip().lower()
_SCHEME_NAME_FRAGMENTS = (
    "панорамное просвечивание",
    "кольцевого сварного соединения",
)
_SCHEME_PARAM_FRAGMENTS = ("схема просвечивания",)
_DISTANCE_PARAM_FRAGMENTS = (
    "расстояние от иии до поверхности",
    "контролируемого сварного соединения",
)
_NOMINAL_DIAMETER_FRAGMENTS = ("номинальный диаметр трубы",)
_WALL_THICKNESS_FRAGMENTS = ("номинальная толщина стенки",)
_SENSITIVITY_FRAGMENTS = ("чувствительность контроля",)
_NUMBER_PATTERN = re.compile(r"-?\d+(?:[.,]\d+)?|-?\d*[.,]\d+")


def _normalize_text(value) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


def scheme_selection_label(value):
    """Текст выбранной схемы из val (строка или {name, val})."""
    if value is None or isinstance(value, (list, tuple)):
        return None
    if isinstance(value, dict):
        v = value.get("name") or value.get("val")
        if isinstance(v, (list, tuple)):
            return None
        return v
    return value


def is_ellipse_frontal_scheme_value(value) -> bool:
    """Схема 7.3: фронтальное просвечивание «на эллипс» (не путать с 7.2)."""
    n = _normalize_text(scheme_selection_label(value))
    if not n:
        return False
    return "фронтальное просвечивание" in n and "на эллипс" in n


def _non_empty_text(value) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None


def _apparatus_display_value(row: dict) -> str | None:
    return _non_empty_text(row.get("val")) or _non_empty_text(row.get("name"))


def _catalog_entry(row: dict) -> dict | None:
    display_value = _apparatus_display_value(row)
    if display_value is None:
        return None
    return {"id": row.get("id"), "name": display_value}


def _find_existing_param_name(
    data: TechCardData, block_name: str, param_names
) -> str | None:
    names = (param_names,) if isinstance(param_names, str) else tuple(param_names)
    for param_name in names:
        if data.has_block_and_param(block_name, param_name):
            return param_name
    return None


def _get_param_dict(data: TechCardData, block_name: str, param_names):
    names = (param_names,) if isinstance(param_names, str) else tuple(param_names)
    if not data.has_block(block_name):
        return None

    for name in names:
        if not data.has_block_and_param(block_name, name):
            continue
        for block in data.params.values():
            if block.get("name") != block_name:
                continue
            for param in block.get("params", {}).values():
                if param.get("name") == name:
                    return param
    return None


def _find_first_param(
    data: TechCardData,
    *,
    exact_names=(),
    name_fragments=(),
    block_name: str | None = None,
):
    exact_set = {
        _normalize_text(name)
        for name in ((exact_names,) if isinstance(exact_names, str) else tuple(exact_names))
        if name
    }
    fragments = tuple(_normalize_text(fragment) for fragment in name_fragments if fragment)

    for block in data.params.values():
        current_block_name = block.get("name")
        if not current_block_name:
            continue
        if block_name and current_block_name != block_name:
            continue
        for param in block.get("params", {}).values():
            param_name = param.get("name")
            normalized_name = _normalize_text(param_name)
            if not normalized_name:
                continue
            if normalized_name in exact_set:
                return current_block_name, param_name, param
            if fragments and all(fragment in normalized_name for fragment in fragments):
                return current_block_name, param_name, param
    return None


def _get_first_param_value(data: TechCardData, param_names=None, name_fragments=(), block_name: str | None = None):
    match = _find_first_param(
        data,
        exact_names=param_names or (),
        name_fragments=name_fragments,
        block_name=block_name,
    )
    if match is None:
        return None
    found_block_name, found_param_name, _ = match
    return data.get_param_value(found_block_name, found_param_name)


def _ensure_apparatus_param_name(data: TechCardData) -> str:
    if data.has_block_and_param(BLOCK_SOURCE, PARAM_APPARATUS):
        return PARAM_APPARATUS
    if data.has_block_and_param(BLOCK_SOURCE, LEGACY_PARAM_APPARATUS):
        data.update_param(
            BLOCK_SOURCE,
            LEGACY_PARAM_APPARATUS,
            {"name": PARAM_APPARATUS},
        )
    return PARAM_APPARATUS


def _parse_decimal(value) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (list, tuple)):
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None

    raw = str(value).strip().replace(",", ".")
    if not raw:
        return None

    try:
        return Decimal(raw)
    except (InvalidOperation, ValueError):
        return None


def _parse_focal_spot_max(value) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (list, tuple)):
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None

    raw = str(value).strip()
    if not raw:
        return None

    normalized = (
        raw.replace(",", ".")
        .replace("×", "x")
        .replace("*", "x")
        .replace("X", "x")
        .replace("Х", "x")
        .replace("х", "x")
    )
    values = []
    for token in _NUMBER_PATTERN.findall(normalized):
        try:
            values.append(Decimal(token.replace(",", ".")))
        except (InvalidOperation, ValueError):
            continue
    if not values:
        return None
    return max(values)


def _parse_selected_id(param_dict) -> int | None:
    if not param_dict:
        return None
    selected_id = param_dict.get("selectedId")
    if selected_id in (None, ""):
        return None
    try:
        return int(selected_id)
    except (TypeError, ValueError):
        return None


def _is_target_scheme_selected(value) -> bool:
    normalized_value = _normalize_text(value)
    if not normalized_value:
        return False
    if normalized_value == _TARGET_SCHEME_KEY:
        return True
    return all(fragment in normalized_value for fragment in _SCHEME_NAME_FRAGMENTS)


def _format_decimal(value: Decimal) -> str:
    rounded = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    text = format(rounded, "f").rstrip("0").rstrip(".")
    return text or "0"


def _set_or_insert_param(
    data: TechCardData,
    param_name: str,
    value,
    insert_id: int,
    aliases=(),
    extra_fields: dict | None = None,
) -> None:
    actual_name = _find_existing_param_name(
        data, BLOCK_SOURCE, (param_name,) + tuple(aliases)
    )
    fields = {"val": value}
    if extra_fields:
        fields.update(extra_fields)

    if actual_name is not None:
        data.update_param(BLOCK_SOURCE, actual_name, fields)
        return

    data.insert_param_to_block(
        BLOCK_SOURCE,
        insert_id,
        {"name": param_name, **fields},
    )


def _clear_param_value(data: TechCardData, param_names) -> None:
    actual_name = _find_existing_param_name(data, BLOCK_SOURCE, param_names)
    if actual_name is None:
        return
    data.set_param_value(BLOCK_SOURCE, actual_name, None)


def _set_distance_placeholder(data: TechCardData, placeholder: str | None) -> None:
    match = _find_first_param(
        data,
        exact_names=PARAM_DISTANCE_NAMES,
        name_fragments=_DISTANCE_PARAM_FRAGMENTS,
        block_name=BLOCK_SOURCE,
    )
    if match is None:
        return
    _, actual_name, _ = match
    # Фронт может читать hint вместо placeholder — дублируем.
    data.update_param(
        BLOCK_SOURCE,
        actual_name,
        {"placeholder": placeholder, "hint": placeholder},
    )


def _build_allowed_apparatus(rows, sensitivity: Decimal, outer_diameter: Decimal, inner_diameter: Decimal):
    allowed = []
    delta = outer_diameter - inner_diameter
    if delta <= 0:
        return allowed

    main_limit = (sensitivity * inner_diameter) / (Decimal("2") * delta)
    relaxed_limit = (sensitivity * inner_diameter) / delta

    for row in rows:
        focal_spot = _parse_focal_spot_max(row.get("focal_spot_size"))
        if focal_spot is None:
            continue

        if focal_spot <= main_limit:
            allowed.append(
                {
                    "row": row,
                    "focal_spot": focal_spot,
                    "requires_source_side_etalon": False,
                }
            )
            continue

        if focal_spot <= relaxed_limit:
            allowed.append(
                {
                    "row": row,
                    "focal_spot": focal_spot,
                    # Future: persist this flag when the card model gets a dedicated field.
                    "requires_source_side_etalon": True,
                }
            )

    return allowed


def _find_matching_allowed_apparatus(
    selected_value,
    apparatus_param_dict,
    allowed_apparatus,
):
    selected_id = _parse_selected_id(apparatus_param_dict)
    if selected_id is not None:
        for entry in allowed_apparatus:
            row_id = entry["row"].get("id")
            try:
                if row_id is not None and int(row_id) == selected_id:
                    return entry
            except (TypeError, ValueError):
                continue

    normalized_selected = _normalize_text(selected_value)
    if not normalized_selected:
        return None

    for entry in allowed_apparatus:
        row = entry["row"]
        candidates = (
            _apparatus_display_value(row),
            _non_empty_text(row.get("name")),
            _non_empty_text(row.get("val")),
        )
        if any(_normalize_text(candidate) == normalized_selected for candidate in candidates):
            return entry

    return None


class RengenApparatusForPanoramicScheme(IDataChanger[TechCardData]):
    """
    Для схемы 7.1 фильтрует допустимые ИИИ по фокусному пятну и,
    после выбора подходящего аппарата, подставляет его параметры и
    расчётную подсказку для расстояния f.
    """

    def __init__(self, db: IRengenApparatusDB):
        self._db = db

    def changeData(self, data: TechCardData) -> TechCardData:
        if not data.has_block(BLOCK_SOURCE):
            _set_distance_placeholder(data, None)
            return data

        scheme_value = _get_first_param_value(
            data,
            PARAM_SCHEME,
            _SCHEME_PARAM_FRAGMENTS,
            BLOCK_SOURCE,
        )
        if not _is_target_scheme_selected(scheme_value):
            _set_distance_placeholder(data, None)
            return data

        outer_diameter = _parse_decimal(
            _get_first_param_value(
                data,
                PARAM_NOMINAL_DIAMETER,
                _NOMINAL_DIAMETER_FRAGMENTS,
            )
        )
        wall_thickness = _parse_decimal(
            _get_first_param_value(
                data,
                PARAM_WALL_THICKNESS,
                _WALL_THICKNESS_FRAGMENTS,
            )
        )
        sensitivity = _parse_decimal(
            _get_first_param_value(
                data,
                SENSITIVITY_PARAM_NAMES,
                _SENSITIVITY_FRAGMENTS,
            )
        )

        if (
            outer_diameter is None
            or wall_thickness is None
            or sensitivity is None
            or outer_diameter <= 0
            or wall_thickness < 0
            or sensitivity <= 0
        ):
            _set_distance_placeholder(data, None)
            return data

        inner_diameter = outer_diameter - (Decimal("2") * wall_thickness)
        if inner_diameter <= 0 or outer_diameter <= inner_diameter:
            _set_distance_placeholder(data, None)
            return data

        if (inner_diameter / outer_diameter) < Decimal("0.8"):
            _set_distance_placeholder(data, None)
            return data

        rows = self._db.get_rengen_apparatus()
        if not rows:
            _set_distance_placeholder(data, None)
            return data

        allowed_apparatus = _build_allowed_apparatus(
            rows, sensitivity, outer_diameter, inner_diameter
        )
        options = [
            option
            for option in (_catalog_entry(entry["row"]) for entry in allowed_apparatus)
            if option is not None
        ]

        apparatus_param_name = _ensure_apparatus_param_name(data)
        apparatus_value = None
        if data.has_block_and_param(BLOCK_SOURCE, apparatus_param_name):
            apparatus_value = data.get_param_value(BLOCK_SOURCE, apparatus_param_name)
        apparatus_param_dict = _get_param_dict(data, BLOCK_SOURCE, apparatus_param_name)

        matched_apparatus = None
        if is_scalar_choice(apparatus_value):
            matched_apparatus = _find_matching_allowed_apparatus(
                apparatus_value,
                apparatus_param_dict,
                allowed_apparatus,
            )

        if matched_apparatus is None:
            _set_or_insert_param(
                data,
                PARAM_APPARATUS,
                None,
                7,
                aliases=(LEGACY_PARAM_APPARATUS,),
                extra_fields={"options": options, "selectedId": None},
            )
            _clear_param_value(data, PARAM_FOCAL_SPOT)
            _clear_param_value(data, (PARAM_VOLTAGE, ALT_PARAM_VOLTAGE))
            _set_distance_placeholder(data, None)
            return data

        selected_row = matched_apparatus["row"]
        selected_display_value = _apparatus_display_value(selected_row)
        selected_row_id = selected_row.get("id")

        _set_or_insert_param(
            data,
            PARAM_APPARATUS,
            selected_display_value,
            7,
            aliases=(LEGACY_PARAM_APPARATUS,),
            extra_fields={
                "options": options,
                "selectedId": (
                    str(selected_row_id)
                    if selected_row_id is not None
                    else None
                ),
            },
        )
        _set_or_insert_param(
            data,
            PARAM_FOCAL_SPOT,
            selected_row.get("focal_spot_size"),
            8,
        )
        _set_or_insert_param(
            data,
            PARAM_VOLTAGE,
            selected_row.get("voltage_on_tube"),
            9,
            aliases=(ALT_PARAM_VOLTAGE,),
        )

        focal_spot = matched_apparatus["focal_spot"]
        distance_min = (focal_spot * (outer_diameter - inner_diameter)) / sensitivity
        distance_max = inner_diameter / Decimal("2")
        _set_distance_placeholder(
            data,
            f"{_format_decimal(distance_min)}<f<={_format_decimal(distance_max)}",
        )
        return data
