from typing import Optional, Tuple

from repositories.Interfaces.i_radiographic_film_db import IRadiographicFilmDB
from services.Interfaces.i_dataChanger import IDataChanger
from services.Changers.param_choice import is_scalar_choice
from services.tech_card import TechCardData


BLOCK_GENERAL = "ОПЕРАЦИОННАЯ ТЕХНОЛОГИЧЕСКАЯ КАРТА РАДИОГРАФИЧЕСКОГО КОНТРОЛЯ СВАРНЫХ СОЕДИНЕНИЙ"
BLOCK_SOURCE = "ИСХОДНЫЕ ДАННЫЕ"

PARAM_QUALITY = "Уровень качества"
PARAM_RAD_THICKNESS = "Радиационная толщина, мм"
PARAM_FILM = "Тип радиографической пленки D-7 (AGFA)"


def _parse_quality(value) -> Optional[str]:
    if not is_scalar_choice(value):
        return None
    s = str(value).strip().upper()
    if s in ("A", "B", "C"):
        return s
    return None


def _parse_thickness_mm(value) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return None


def _class_range_for_xray(quality: str, thickness_mm: float) -> Optional[Tuple[int, int]]:
    # Таблица из изображения для рентгеновского излучения.
    if thickness_mm <= 3.0:
        return {"A": (1, 3), "B": (1, 2), "C": (1, 3)}.get(quality)
    if thickness_mm <= 12.0:
        return {"A": (1, 3), "B": (1, 2), "C": (1, 3)}.get(quality)
    if thickness_mm <= 20.0:
        return {"A": (1, 6), "B": (1, 2), "C": (1, 6)}.get(quality)

    return {"A": (1, 6), "B": (1, 3), "C": (1, 6)}.get(quality)
    


class RadiographicFilmFromDb(IDataChanger[TechCardData]):
    """
    Меняет только значение существующего поля
    «Тип радиографической пленки D-7 (AGFA)».
    Новых полей не добавляет.
    """

    def __init__(self, db: IRadiographicFilmDB):
        self._db = db

    def changeData(self, data: TechCardData) -> TechCardData:
        if not data.has_block_and_param(BLOCK_SOURCE, PARAM_FILM):
            return data
        if not data.has_block_and_param(BLOCK_GENERAL, PARAM_QUALITY):
            return data
        if not data.has_block_and_param(BLOCK_SOURCE, PARAM_RAD_THICKNESS):
            return data

        quality = _parse_quality(data.get_param_value(BLOCK_GENERAL, PARAM_QUALITY))
        thickness_mm = _parse_thickness_mm(
            data.get_param_value(BLOCK_SOURCE, PARAM_RAD_THICKNESS)
        )
        if quality is None or thickness_mm is None:
            return data

        class_range = _class_range_for_xray(quality, thickness_mm)
        if class_range is None:
            return data

        film = self._db.get_radiographic_film_by_class_range(
            class_range[0], class_range[1]
        )
        if not film:
            return data

        film_name = str(film.get("name") or "").strip()
        if not film_name:
            return data

        data.set_param_value(BLOCK_SOURCE, PARAM_FILM, film_name)
        return data

