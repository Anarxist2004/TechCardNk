from services.Interfaces.i_dataChanger import IDataChanger
from services.tech_card import TechCardData
from repositories.Interfaces.i_radiographic_film_db import IRadiographicFilmDB

def _parse_float_value(val) -> float | None:
    """Преобразует значение в float, если возможно."""
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _get_quality_class(val) -> str | None:
    """Получает класс качества (А, В, С) из значения параметра."""
    if not val:
        return None
    s = str(val).strip().upper()
    if s in ('A', 'А', 'CLASS A', 'КЛАСС А'):
        return 'A'
    if s in ('B', 'В', 'CLASS B', 'КЛАСС В'):
        return 'B'
    if s in ('C', 'С', 'CLASS C', 'КЛАСС С'):
        return 'C'
    return None


def _determine_film_class(radiation_thickness: float, quality_class: str) -> list[int] | None:
    """
    Определяет классы радиографической плёнки на основе радиационной толщины и класса качества.
    
    Возвращает список классов плёнки (может быть несколько, например [1, 2] или [1, 2, 3]).
    """
    if radiation_thickness is None or quality_class is None:
        return None
    
    # Таблица соответствий
    # Формат: (максимальная толщина, класс качества, классы плёнки)
    rules = [
        # До 3.0 мм
        (3.0, 'A', [1, 2, 3]),
        (3.0, 'B', [1, 2]),
        (3.0, 'C', [1, 2, 3]),
        
        # Свыше 3.0 до 12 мм (рентгеновское излучение)
        (12.0, 'A', [1, 2, 3]),
        (12.0, 'B', [1, 2]),
        (12.0, 'C', [1, 2, 3]),
        
        # Свыше 12 до 20 мм
        (20.0, 'A', [1, 2, 3]),
        (20.0, 'B', [1, 2, 3]),
        (20.0, 'C', [1, 2, 3]),
        
        # Свыше 20 до 40 мм
        (40.0, 'A', [1, 2, 3]),
        (40.0, 'B', [1, 2, 3]),
        (40.0, 'C', [1, 2, 3]),
    ]
    
    # Применяем правила
    for max_thickness, cls, film_classes in rules:
        if radiation_thickness <= max_thickness and quality_class == cls:
            return film_classes
    
    # Если толщина больше 40 мм
    if radiation_thickness > 40.0:
        # По умолчанию все классы, но можно добавить специальную логику
        return [1, 2, 3]
    
    return None


class getRadiograficFilm(IDataChanger[TechCardData]):
    """
    Чейнджер для определения класса радиографической плёнки на основе:
    - радиационной толщины
    - уровня качества (А, В, С)
    
    Результат используется для выбора радиографической плёнки.
    """

    BLOCK_SOURCE = "ИСХОДНЫЕ ДАННЫЕ"  # или другой блок, где лежат эти параметры
    BLOCK_FIRST="ОПЕРАЦИОННАЯ ТЕХНОЛОГИЧЕСКАЯ КАРТА РАДИОГРАФИЧЕСКОГО КОНТРОЛЯ СВАРНЫХ СОЕДИНЕНИЙ"
    PARAM_RADIATION_THICKNESS = "Радиационная толщина, мм"
    PARAM_QUALITY_CLASS = "Уровень качества"
    PARAM_FILM_CLASS = "Тип радиографической пленки"
    PARAM_FILM_CLASS_LEGACY = "Тип радиографической"

    def __init__(self, db: IRadiographicFilmDB):
        self._db = db

    def changeData(self, data: TechCardData) -> TechCardData:
        # Проверяем наличие необходимых блоков и параметров
        if not data.has_block(self.BLOCK_SOURCE):
            return data
        
        # Получаем радиационную толщину
        if not data.has_block_and_param(self.BLOCK_SOURCE, self.PARAM_RADIATION_THICKNESS):
            return data
        
        # Получаем уровень качества
        if not data.has_block_and_param(self.BLOCK_FIRST, self.PARAM_QUALITY_CLASS):
            return data
        
        # Извлекаем значения
        thickness_val = data.get_param_value(self.BLOCK_SOURCE, self.PARAM_RADIATION_THICKNESS)
        # Уровень качества берём из того же блока, в котором его проверяли
        quality_val = data.get_param_value(self.BLOCK_FIRST, self.PARAM_QUALITY_CLASS)
        
        # Преобразуем в нужные типы
        thickness = _parse_float_value(thickness_val)
        quality_class = _get_quality_class(quality_val)
        
        if thickness is None or quality_class is None:
            # Недостаточно данных для определения класса плёнки
            return data
        
        # Определяем возможные классы плёнки
        film_classes = _determine_film_class(thickness, quality_class)
        
        if not film_classes:
            # Не удалось определить классы плёнки
            return data
        
        # Получаем список плёнок из БД по определённым классам
        films = self._db.get_films_by_classes(film_classes)
        
        # Формируем параметр с выбором плёнки
        options = [
            {
                "id": film["id"],
                "name": film["name"],
                "film_class": film.get("film_class")
            }
            for film in films
        ]
        
        # Определяем, какой параметр обновлять:
        # 1) новый ("Тип радиографической пленки"),
        # 2) или старый из шаблона ("Тип радиографической"), чтобы не плодить дубликаты.
        target_name = None
        if data.has_block_and_param(self.BLOCK_SOURCE, self.PARAM_FILM_CLASS):
            target_name = self.PARAM_FILM_CLASS
        elif data.has_block_and_param(self.BLOCK_SOURCE, self.PARAM_FILM_CLASS_LEGACY):
            target_name = self.PARAM_FILM_CLASS_LEGACY

        if target_name is not None:
            # Обновляем существующий параметр, не меняя его позиции
            data.update_param(
                self.BLOCK_SOURCE,
                target_name,
                {"options": options}
            )
        else:
            # Параметра ещё нет в блоке — добавляем в конец
            data.add_param_to_block(
                self.BLOCK_SOURCE,
                {
                    "name": self.PARAM_FILM_CLASS,
                    "val": None,
                    "options": options,
                    "typeData": "string",
                    "displayMode": None,
                }
            )
        
        return data