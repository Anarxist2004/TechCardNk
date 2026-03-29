from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union


class IParamsByTypeWeldingJointDB(ABC):
    """Дополнительные параметры по типу сварного соединения (params_by_type_welding_joint)."""

    @abstractmethod
    def get_params_by_welded_joint_type(
        self, joint_name_or_id: Union[str, int]
    ) -> List[Dict[str, Any]]:
        """Список записей: id, name, subtitle для выбранного типа соединения, порядок по id."""
        pass
