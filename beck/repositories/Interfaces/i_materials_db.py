from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IMaterialsDB(ABC):
    """Материалы из type_metall."""

    @abstractmethod
    def get_materials(self) -> List[Dict[str, Any]]:
        """Список записей материалов как минимум с полями id, material."""
        pass
