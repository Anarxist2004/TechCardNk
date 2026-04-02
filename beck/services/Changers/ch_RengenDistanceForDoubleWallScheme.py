from decimal import Decimal

from services.Changers.ch_RengenApparatusForPanoramicScheme import (
    BLOCK_SOURCE,
    PARAM_FOCAL_SPOT,
    PARAM_NOMINAL_DIAMETER,
    PARAM_SCHEME,
    PARAM_WALL_THICKNESS,
    SENSITIVITY_PARAM_NAMES,
    _NOMINAL_DIAMETER_FRAGMENTS,
    _SCHEME_PARAM_FRAGMENTS,
    _SENSITIVITY_FRAGMENTS,
    _WALL_THICKNESS_FRAGMENTS,
    _find_first_param,
    _format_decimal,
    _get_first_param_value,
    _normalize_text,
    _parse_decimal,
    _parse_focal_spot_max,
    _set_distance_placeholder,
)
from services.Interfaces.i_dataChanger import IDataChanger
from services.tech_card import TechCardData


TARGET_SCHEME = "Кольцевое сварное соединение через две стенки"
QUALITY_PARAM_NAME = "Уровень качества"
_TARGET_SCHEME_FRAGMENTS = (
    "кольцевое сварное соединение",
    "через две стенки",
)
_QUALITY_PARAM_FRAGMENTS = ("уровень качества",)
QUALITY_TO_S_FACTOR = {
    "A": Decimal("1.2"),
    "B": Decimal("1.1"),
    "C": Decimal("1.5"),
}


def _parse_quality(value) -> str | None:
    if value is None or isinstance(value, (list, tuple)):
        return None

    normalized = _normalize_text(value).upper()
    return normalized if normalized in QUALITY_TO_S_FACTOR else None


def _is_target_scheme(value) -> bool:
    normalized = _normalize_text(value)
    if not normalized:
        return False
    if normalized == _normalize_text(TARGET_SCHEME):
        return True
    return all(fragment in normalized for fragment in _TARGET_SCHEME_FRAGMENTS)


def _resolve_c_factor(quality: str, radiation_thickness: Decimal) -> Decimal | None:
    if quality == "A":
        return Decimal("2") if radiation_thickness <= Decimal("100") else Decimal("3")
    if quality == "B":
        if radiation_thickness <= Decimal("50"):
            return Decimal("2")
        if radiation_thickness <= Decimal("100"):
            return Decimal("3")
        return Decimal("4")
    if quality == "C":
        return Decimal("2")
    return None


class RengenDistanceForDoubleWallScheme(IDataChanger[TechCardData]):
    """
    Для схемы 7.2 рассчитывает нижнюю границу f после выбора аппарата и
    обновляет placeholder поля расстояния до контролируемого соединения.
    """

    def changeData(self, data: TechCardData) -> TechCardData:
        scheme_value = _get_first_param_value(
            data,
            PARAM_SCHEME,
            _SCHEME_PARAM_FRAGMENTS,
            BLOCK_SOURCE,
        )
        if not _is_target_scheme(scheme_value):
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
        focal_spot = _parse_focal_spot_max(
            _get_first_param_value(data, PARAM_FOCAL_SPOT)
        )

        quality_match = _find_first_param(
            data,
            exact_names=QUALITY_PARAM_NAME,
            name_fragments=_QUALITY_PARAM_FRAGMENTS,
        )
        quality_value = None
        if quality_match is not None:
            block_name, param_name, _ = quality_match
            quality_value = data.get_param_value(block_name, param_name)
        quality = _parse_quality(quality_value)

        if (
            outer_diameter is None
            or wall_thickness is None
            or sensitivity is None
            or focal_spot is None
            or quality is None
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

        s_factor = QUALITY_TO_S_FACTOR.get(quality)
        radiation_thickness = wall_thickness * Decimal("2")
        c_factor_multiplier = _resolve_c_factor(quality, radiation_thickness)
        if s_factor is None or c_factor_multiplier is None:
            _set_distance_placeholder(data, None)
            return data

        c_factor = (c_factor_multiplier * focal_spot) / sensitivity
        min_distance = (
            Decimal("1.2") * c_factor * s_factor * wall_thickness
        ) - ((outer_diameter + inner_diameter) / Decimal("2"))
        if min_distance < 0:
            min_distance = Decimal("0")

        _set_distance_placeholder(
            data,
            f"f>={_format_decimal(min_distance)}",
        )
        return data
