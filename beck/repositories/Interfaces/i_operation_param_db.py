from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IOperationParamDB(ABC):
    """Доступ к list_operation и operation_param."""

    @abstractmethod
    def get_operation_params_by_list_id(self, list_id: int) -> List[Dict[str, Any]]:
        """
        Возвращает все параметры операций для выбранного списка.
        Ожидаемые поля в строке: id, id_list, name_param, val, val2.
        """
        pass

