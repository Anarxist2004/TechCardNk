from typing import Any

from controllers.Interfaces.i_controllers import IControllers
from services.Interfaces.i_servise import IServise
from services.tech_card import TechCardData


class ControllerWeb(IControllers[TechCardData]):
    def __init__(self, serv: IServise):
        self.serv = serv

    def get_template(self):
        techCard = self.serv.get_template()
        return techCard.serialise()

    def updateTechCard(self, techCard) -> TechCardData:
        data = TechCardData()
        data.from_jsonDeSerialise(techCard)
        return self.serv.updateTechCard(data)

    def saveTechCard(
        self,
        name: str,
        card_data: dict[str, Any],
        card_id: int | None = None,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        return self.serv.saveTechCard(name, card_data, card_id, user_id)

    def listSavedTechCards(self) -> list[dict[str, Any]]:
        return self.serv.listSavedTechCards()

    def getSavedTechCard(self, card_id: int) -> dict[str, Any] | None:
        return self.serv.getSavedTechCard(card_id)
