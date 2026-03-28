from services.tech_card import TechCardData
from services.PipeLine import PipeLine
from repositories.Interfaces.i_repository import IRepository
from services.Interfaces.i_servise import IServise


class TechCardService(IServise):
    GAZPROM_METHODOLOGY = 1
    GAZPROM_OPERATIONAL_METHODOLOGY = 2

    METHODOLOGIES = {
        GAZPROM_METHODOLOGY: "Газпром",
        GAZPROM_OPERATIONAL_METHODOLOGY: "Газпром 2",
    }

    def __init__(self, repos: dict[int, IRepository], piLine: PipeLine):
        self.repos = repos
        self.pipeLine = piLine

    def _normalise_methodology(self, methodology) -> int:
        try:
            methodology_id = int(methodology)
        except (TypeError, ValueError):
            methodology_id = self.GAZPROM_METHODOLOGY

        if methodology_id not in self.repos:
            return self.GAZPROM_METHODOLOGY

        return methodology_id

    def _get_repo(self, methodology) -> IRepository:
        methodology_id = self._normalise_methodology(methodology)
        return self.repos[methodology_id]

    def findNewParamsByTechCard(self, data: TechCardData) -> None:
        _ = data
        return

    def setData(self, data: TechCardData) -> None:
        _ = data

    def getObjectControl(self, methodology=0) -> TechCardData:
        repo = self._get_repo(methodology)
        return repo.get_all_controlled_element_types()

    def getControlElements(self, id, methodology=0) -> TechCardData:
        repo = self._get_repo(methodology)
        return repo.get_all_objects_by_type_id(id)

    def getControlElementParam(self, id, methodology=0) -> TechCardData:
        methodology_id = self._normalise_methodology(methodology)
        repo = self._get_repo(methodology_id)
        tech_card = repo.get_params_for_type(id)
        self.pipeLine.process(tech_card, methodology_id)
        return tech_card

    def getControlElementParamValue(self, idCntlEl, idParam) -> TechCardData:
        repo = self._get_repo(self.GAZPROM_METHODOLOGY)
        return repo.get_all_possible_values_by_param_and_element(idCntlEl, idParam)

    def geElementParamsValue(self, id, methodology=0) -> TechCardData:
        methodology_id = self._normalise_methodology(methodology)
        repo = self._get_repo(methodology_id)
        tech_card = repo.get_params_for_element(id)
        self.pipeLine.process(tech_card, methodology_id)
        return tech_card

    def updateTechCard(self, techCard) -> TechCardData:
        methodology_id = self._normalise_methodology(techCard.getMethodology())
        repo = self._get_repo(methodology_id)
        techCard.methodology = methodology_id
        techCard = repo.sync_tech_card(techCard)
        self.pipeLine.process(techCard, methodology_id)
        return techCard

    def getMethodologies(self) -> dict[int, str]:
        return dict(self.METHODOLOGIES)

    def createParamOption(self, payload) -> dict:
        methodology = self.GAZPROM_METHODOLOGY
        if isinstance(payload, dict):
            methodology = payload.get("methodology", self.GAZPROM_METHODOLOGY)

        repo = self._get_repo(methodology)
        return repo.create_param_option(payload if isinstance(payload, dict) else {})
