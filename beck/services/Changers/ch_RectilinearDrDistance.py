"""
Цифровая радиография, прямолинейное (и близкое к прямолинейному) сварное соединение.

По СТО Газпром (разд. 9.5.x): f = c · S · (t + b), где c = n·Φ/K;
n и S зависят от класса изображения (SA-R / SB-R / SC-R — в техкарте: A / B / C)
и радиационной толщины t; b — расстояние от ППД до поверхности металла.

Дополнительно: f не ниже 4·(t + b), если это даёт большее значение, чем c·S·(t+b).

Подсказка для поля расстояния: f≥X (как у других схем).
"""
from decimal import Decimal

from services.Changers.ch_RengenApparatusForPanoramicScheme import (
    BLOCK_SOURCE,
    PARAM_FOCAL_SPOT,
    PARAM_SCHEME,
    SENSITIVITY_PARAM_NAMES,
    _SCHEME_PARAM_FRAGMENTS,
    _SENSITIVITY_FRAGMENTS,
    _find_first_param,
    _format_decimal,
    _get_first_param_value,
    _normalize_text,
    _parse_decimal,
    _parse_focal_spot_max,
    _set_distance_placeholder,
    scheme_selection_label,
)
from services.Interfaces.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

from services.Changers.ch_RengenDistanceForDoubleWallScheme import (
    QUALITY_PARAM_NAME,
    _QUALITY_PARAM_FRAGMENTS,
    _parse_quality,
)

PARAM_RAD_THICKNESS = "Радиационная толщина, мм"
# Если в техкарте появится отдельное поле — подхватится; иначе b = 0
_DETECTOR_DISTANCE_FRAGMENTS = ("детектор", "поверхност")

QUALITY_TO_S_IMAGE = {
    "A": Decimal("1.2"),  # SA-R
    "B": Decimal("1.1"),  # SB-R
    "C": Decimal("1.5"),  # SC-R
}


def is_rectilinear_scheme_value(value) -> bool:
    """Схема «Прямолинейное сварное соединение» (ЦР)."""
    label = scheme_selection_label(value)
    n = _normalize_text(label)
    if not n:
        return False
    return "прямолинейн" in n and "сварн" in n


def _n_phi_over_k_divisor(quality: str, t_mm: Decimal) -> int | None:
    """
    Множитель n в c = n·Φ/K по классу изображения и толщине t (мм).
    SA-R / SB-R / SC-R ↔ A / B / C.
    """
    if quality == "A":
        if t_mm < Decimal("50"):
            return 2
        if t_mm <= Decimal("100"):
            return 3
        return 4
    if quality == "B":
        if t_mm <= Decimal("100"):
            return 2
        return 3
    if quality == "C":
        return 2
    return None


class RectilinearDrDistance(IDataChanger[TechCardData]):
    """
    Расстояние от ИИИ до поверхности для прямолинейного шва (ЦР):
    f ≥ max( c·S·(t+b), 4·(t+b) ), c = n·Φ/K.
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
        if not is_rectilinear_scheme_value(scheme_value):
            return data

        t_mm = _parse_decimal(
            _get_first_param_value(
                data,
                PARAM_RAD_THICKNESS,
                (),
                BLOCK_SOURCE,
            )
        )
        focal_raw = _get_first_param_value(data, PARAM_FOCAL_SPOT)
        phi = _parse_focal_spot_max(focal_raw)

        sens_raw = _get_first_param_value(
            data,
            SENSITIVITY_PARAM_NAMES,
            _SENSITIVITY_FRAGMENTS,
        )
        k_mm = _parse_decimal(sens_raw)

        q_match = _find_first_param(
            data,
            exact_names=QUALITY_PARAM_NAME,
            name_fragments=_QUALITY_PARAM_FRAGMENTS,
        )
        quality_val = None
        if q_match is not None:
            bn, pn, _ = q_match
            quality_val = data.get_param_value(bn, pn)
        quality = _parse_quality(quality_val)

        b_match = _find_first_param(
            data,
            exact_names=(),
            name_fragments=_DETECTOR_DISTANCE_FRAGMENTS,
            block_name=BLOCK_SOURCE,
        )
        b_mm = Decimal("0")
        if b_match is not None:
            bv = _parse_decimal(data.get_param_value(b_match[0], b_match[1]))
            if bv is not None and bv >= 0:
                b_mm = bv

        if (
            t_mm is None
            or phi is None
            or k_mm is None
            or quality is None
            or t_mm <= 0
            or k_mm <= 0
        ):
            _set_distance_placeholder(data, None)
            return data

        n = _n_phi_over_k_divisor(quality, t_mm)
        s_img = QUALITY_TO_S_IMAGE.get(quality)
        if n is None or s_img is None:
            _set_distance_placeholder(data, None)
            return data

        t_sum = t_mm + b_mm
        if t_sum <= 0:
            _set_distance_placeholder(data, None)
            return data

        # c = n·Φ/K; f_sto = c·S·(t+b) = n·Φ·S·(t+b)/K
        f_sto = (Decimal(n) * phi * s_img * t_sum) / k_mm
        f_four = Decimal("4") * t_sum
        f_min = f_sto if f_sto >= f_four else f_four
        l_exposure_max = f_min * Decimal("0.8")
        hint = (
            f"f≥{_format_decimal(f_min)}; "
            f"Lуч≤{_format_decimal(l_exposure_max)} (п. 9.5.21)"
        )
        _set_distance_placeholder(data, hint)
        return data
