from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    def __init__(self):
        return

    @abstractmethod
    def get_operation_params_by_list_id(self, list_id: int) -> List[Dict[str, Any]]:
        """Параметры операций для блока «ПЕРЕЧЕНЬ ОПЕРАЦИЙ РК»."""
        pass

    @abstractmethod
    def save_tech_card_snapshot(
        self, name: str, card_data: Dict[str, Any], card_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Сохранить снапшот техкарты (insert/update)."""
        pass

    @abstractmethod
    def list_saved_tech_cards(self) -> List[Dict[str, Any]]:
        """Список сохранённых техкарт."""
        pass

    @abstractmethod
    def get_saved_tech_card(self, card_id: int) -> Optional[Dict[str, Any]]:
        """Одна сохранённая техкарта по id."""
        pass