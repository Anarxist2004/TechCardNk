from abc import ABC, abstractmethod
from typing import Any

from services.tech_card import TechCardData


class IServise(ABC):
    @abstractmethod
    def get_template(self) -> TechCardData:
        pass

    @abstractmethod
    def updateTechCard(self, data) -> TechCardData:
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
    def listSavedTechCardImages(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def getSavedTechCard(self, card_id: int) -> dict[str, Any] | None:
        pass
