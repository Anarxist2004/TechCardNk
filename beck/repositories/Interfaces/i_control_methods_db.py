from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IControlMethodsDB(ABC):
    """Интерфейс доступа к данным о методах контроля в БД."""

    @abstractmethod
    def get_control_methods(self) -> List[Dict[str, Any]]:
        """Возвращает записи методов контроля (как минимум поля id, name)."""
        pass
