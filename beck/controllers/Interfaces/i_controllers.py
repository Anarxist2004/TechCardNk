from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from services.tech_card import TechCardData


T = TypeVar("T")


class IControllers(ABC, Generic[T]):
    @abstractmethod
    def get_template(self) -> TechCardData:
        pass

    @abstractmethod
    def updateTechCard(self, techCard) -> TechCardData:
        pass

    @abstractmethod
    def saveTechCard(
        self,
        name: str,
        card_data: dict[str, Any],
        card_id: int | None = None,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def listSavedTechCards(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def getSavedTechCard(self, card_id: int) -> dict[str, Any] | None:
        pass
