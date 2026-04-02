from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class IRengenApparatusDB(ABC):
    """Доступ к данным рентген-аппаратов из rengen_apparatus."""

    @abstractmethod
    def get_rengen_apparatus(self) -> List[Dict[str, Any]]:
        """Все записи rengen_apparatus: как минимум id, name, val, focal_spot_size, voltage_on_tube."""
        pass

    @abstractmethod
    def get_rengen_apparatus_by_name_or_id(
        self, apparatus_name_or_id: Union[str, int]
    ) -> Optional[Dict[str, Any]]:
        """Одна запись рентген-аппарата по id, name или val."""
        pass
