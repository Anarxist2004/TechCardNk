from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union


class IChemeControlDB(ABC):
    """Схемы контроля (cheme_control) и связь с типом сварного соединения (weld_type_to_scheme)."""

    @abstractmethod
    def get_control_schemes_for_welded_joint(
        self, joint_name_or_id: Union[str, int]
    ) -> List[Dict[str, Any]]:
        """
        Схемы контроля, подходящие для выбранного типа сварного соединения
        (по id или имени записи type_of_welded_joint).
        """
        pass
