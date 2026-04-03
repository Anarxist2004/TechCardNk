from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IRadiographicFilmDB(ABC):
    """Доступ к данным радиографических плёнок из radiographic_film."""

    @abstractmethod
    def get_films_by_classes(self, film_classes: List[int]) -> List[Dict[str, Any]]:
        """Плёнки, у которых film_class входит в переданный список классов.

        Возвращает записи с полями id, film_class, name.
        """
        pass
