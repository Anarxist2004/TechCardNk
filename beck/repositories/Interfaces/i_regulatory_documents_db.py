from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IRegulatoryDocumentsDB(ABC):
    """Интерфейс доступа к нормативным документам в БД."""

    @abstractmethod
    def get_regulatory_documents(self) -> List[Dict[str, Any]]:
        """Все записи (как минимум id, control_methods_id, name)."""
        pass

    @abstractmethod
    def get_regulatory_documents_by_control_method_id(
        self, control_method_id: int
    ) -> List[Dict[str, Any]]:
        """Документы, привязанные к методу контроля по id."""
        pass

    @abstractmethod
    def get_regulatory_documents_for_method_name(
        self, method_name: str
    ) -> List[Dict[str, Any]]:
        """Документы по имени метода контроля (как в control_methods.name)."""
        pass
