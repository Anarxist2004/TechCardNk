from services.tech_card import TechCardData
from services.PipeLine import PipeLine
from interfaces.i_repository import IRepository
from interfaces.i_controllers import IControllers
from interfaces.i_servise import IServise


class TechCardService(IServise):
    ROSATOM_METHODOLOGY = 0
    GAZPROM_METHODOLOGY = 1

    METHODOLOGIES = {
        ROSATOM_METHODOLOGY: "РосАтом",
        GAZPROM_METHODOLOGY: "Газпром",
    }

    def __init__(self, repos: dict[int, IRepository], piLine: PipeLine):
        self.repos = repos
        self.pipeLine = piLine

    def _normalise_methodology(self, methodology) -> int:
        try:
            methodology_id = int(methodology)
        except (TypeError, ValueError):
            methodology_id = self.ROSATOM_METHODOLOGY

        if methodology_id not in self.repos:
            return self.ROSATOM_METHODOLOGY

        return methodology_id

    def _get_repo(self, methodology) -> IRepository:
        methodology_id = self._normalise_methodology(methodology)
        return self.repos[methodology_id]

    def findNewParamsByTechCard(self, data: TechCardData) -> None:
        return

    def setData(self, data: TechCardData) -> None:
        pass

    def getObjectControl(self, methodology=0) -> TechCardData:
        repo = self._get_repo(methodology)
        return repo.get_all_controlled_element_types()

    def getControlElements(self, id, methodology=0) -> TechCardData:
        repo = self._get_repo(methodology)
        return repo.get_all_objects_by_type_id(id)

    def getControlElementParam(self, id, methodology=0) -> TechCardData:
        methodology_id = self._normalise_methodology(methodology)
        repo = self._get_repo(methodology_id)
        techCars = repo.get_params_for_type(id)
        self.pipeLine.process(techCars, methodology_id)
        return techCars

    def getControlElementParamValue(self, idCntlEl, idParam) -> TechCardData:
        repo = self._get_repo(self.ROSATOM_METHODOLOGY)
        return repo.get_all_possible_values_by_param_and_element(idCntlEl, idParam)

    def geElementParamsValue(self, id, methodology=0) -> TechCardData:
        methodology_id = self._normalise_methodology(methodology)
        repo = self._get_repo(methodology_id)
        techCars = repo.get_params_for_element(id)
        self.pipeLine.process(techCars, methodology_id)
        return techCars

    def updateTechCard(self, techCard) -> TechCardData:
        methodology_id = self._normalise_methodology(techCard.getMethodology())
        techCard.methodology = methodology_id
        self.pipeLine.process(techCard, methodology_id)
        return techCard

    def getMethodologies(self) -> dict[int, str]:
        return dict(self.METHODOLOGIES)
