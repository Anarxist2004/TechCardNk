import re
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
        text = str(value).strip().replace(",", ".")
        return float(text)
    except (TypeError, ValueError):
        text = str(value).strip().replace(",", ".")
        match = re.search(r"[-+]?\d*\.?\d+", text)
        if not match:
            return None
        try:
            return float(match.group(0))
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
    if thickness_mm <= 40.0:
        return {"A": (1, 6), "B": (1, 3), "C": (1, 6)}.get(quality)
    # Для толщин > 40 мм в таблице указан диапазон класса B (1-3).
    # Чтобы changer не "молчал", применяем этот диапазон для любого
    # выбранного уровня качества.
    return (1, 3)


def _value_matches_expected(current_value, expected_names: list[str]) -> bool:
    if len(expected_names) == 1:
        expected = expected_names[0]
        if isinstance(current_value, str):
            return current_value.strip() == expected
        if isinstance(current_value, (list, tuple)) and len(current_value) == 1:
            return str(current_value[0]).strip() == expected
        return False

    expected_set = {name.strip() for name in expected_names if str(name).strip()}
    if isinstance(current_value, (list, tuple)):
        current_set = {
            str(item).strip() for item in current_value if str(item).strip()
        }
        return current_set == expected_set
    return False
    


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

        films = self._db.get_radiographic_films_by_class_range(
            class_range[0], class_range[1]
        )
        if not films:
            data.set_param_value(BLOCK_SOURCE, PARAM_FILM, None)
            return data

        names = []
        seen = set()
        for film in films:
            film_name = str(film.get("name") or "").strip()
            if film_name and film_name not in seen:
                seen.add(film_name)
                names.append(film_name)
        if not names:
            data.set_param_value(BLOCK_SOURCE, PARAM_FILM, None)
            return data

        current_value = data.get_param_value(BLOCK_SOURCE, PARAM_FILM)
        if _value_matches_expected(current_value, names):
            return data

        if len(names) == 1:
            data.set_param_value(BLOCK_SOURCE, PARAM_FILM, names[0])
        else:
            data.set_param_value(BLOCK_SOURCE, PARAM_FILM, names)
        return data

