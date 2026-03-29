from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ITypeOfWeldedJointDB(ABC):
    """Интерфейс доступа к типам сварных соединений (type_of_welded_joint)."""

    @abstractmethod
    def get_type_of_welded_joints(self) -> List[Dict[str, Any]]:
        """Все записи (id, regulatory_documents_id, name, image_ref)."""
        pass

    @abstractmethod
    def get_type_of_welded_joints_by_regulatory_document_id(
        self, regulatory_document_id: int
    ) -> List[Dict[str, Any]]:
        """Типы соединений по id нормативного документа."""
        pass

    @abstractmethod
    def get_type_of_welded_joints_for_regulatory_document_name(
        self, regulatory_document_name: str
    ) -> List[Dict[str, Any]]:
        """Типы соединений по имени нормативного документа."""
        pass
