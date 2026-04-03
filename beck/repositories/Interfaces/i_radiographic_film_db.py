from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IRadiographicFilmDB(ABC):
    """Доступ к таблице radiographic_film."""

    @abstractmethod
    def get_radiographic_films(self) -> List[Dict[str, Any]]:
        """Все записи плёнок: id, film_class, name."""
        pass

    @abstractmethod
    def get_radiographic_films_by_class_range(
        self, min_class: int, max_class: int
    ) -> List[Dict[str, Any]]:
        """
        Все плёнки с классом в диапазоне [min_class, max_class].
        """
        pass

