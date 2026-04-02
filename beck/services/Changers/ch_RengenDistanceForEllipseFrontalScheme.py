from decimal import Decimal

from services.Changers.param_choice import is_scalar_choice
from services.Interfaces.i_dataChanger import IDataChanger
from services.tech_card import TechCardData
from services.Changers.ch_RengenDistanceForDoubleWallScheme import (
    QUALITY_PARAM_NAME,
    _QUALITY_PARAM_FRAGMENTS,
    QUALITY_TO_S_FACTOR,
    _parse_quality,
)
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
    _ensure_apparatus_param_name,
    _find_first_param,
    _format_decimal,
    _get_first_param_value,
    _parse_decimal,
    _parse_focal_spot_max,
    _set_distance_placeholder,
    is_ellipse_frontal_scheme_value,
)

class RengenDistanceForEllipseFrontalScheme(IDataChanger[TechCardData]):
    """
    Схема 7.3 (фронтальное просвечивание через две стенки «на эллипс»):
    f >= (2 * Φ * d * S) / K, где d — внутренний диаметр, K — чувствительность,
    S — по классу изображения (A/B/C), Φ — из поля фокусного пятна после выбора ИИИ.

    Подсказка для поля расстояния: f>=X (X >= 0). Без выбранного аппарата / Φ не считаем.
    """

    def changeData(self, data: TechCardData) -> TechCardData:
        if not data.has_block(BLOCK_SOURCE):
            return data

        scheme_value = _get_first_param_value(
            data,
            PARAM_SCHEME,
            _SCHEME_PARAM_FRAGMENTS,
            BLOCK_SOURCE,
        )
        if not is_ellipse_frontal_scheme_value(scheme_value):
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

        apparatus_param_name = _ensure_apparatus_param_name(data)
        apparatus_value = None
        if data.has_block_and_param(BLOCK_SOURCE, apparatus_param_name):
            apparatus_value = data.get_param_value(BLOCK_SOURCE, apparatus_param_name)

        focal_raw = _get_first_param_value(data, PARAM_FOCAL_SPOT)
        focal_spot = _parse_focal_spot_max(focal_raw)

        if (
            outer_diameter is None
            or wall_thickness is None
            or sensitivity is None
            or quality is None
            or outer_diameter <= 0
            or wall_thickness < 0
            or sensitivity <= 0
        ):
            _set_distance_placeholder(data, None)
            return data

        s_factor = QUALITY_TO_S_FACTOR.get(quality)
        if s_factor is None:
            _set_distance_placeholder(data, None)
            return data

        inner_diameter = outer_diameter - (Decimal("2") * wall_thickness)
        if inner_diameter <= 0 or outer_diameter <= inner_diameter:
            _set_distance_placeholder(data, None)
            return data

        if not is_scalar_choice(apparatus_value):
            _set_distance_placeholder(data, None)
            return data

        if focal_spot is None:
            _set_distance_placeholder(data, None)
            return data

        # f >= (2 * Φ * d * S) / K
        f_min = (Decimal("2") * focal_spot * inner_diameter * s_factor) / sensitivity
        if f_min < 0:
            f_min = Decimal("0")

        _set_distance_placeholder(
            data,
            f"f>={_format_decimal(f_min)}",
        )
        return data
