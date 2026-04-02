from abc import ABC, abstractmethod
from typing import Optional, Union


class IMaterialStandardDB(ABC):
    """Доступ к id_standard выбранного материала из type_metall."""

    @abstractmethod
    def get_material_standard_id(
        self, material_name_or_id: Union[str, int]
    ) -> Optional[int]:
        """Возвращает id_standard материала по его имени или id."""
        pass
