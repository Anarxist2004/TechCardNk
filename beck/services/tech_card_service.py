from services.tech_card import TechCardData
from services.PipeLine import PipeLine
from interfaces.i_repository import IRepository
from interfaces.i_controllers import IControllers
from interfaces.i_servise import IServise

class TechCardService(IServise):
    def __init__(self, repo: IRepository,piLine:PipeLine):
        self.repo = repo
        self.pipeLine=piLine
    def findNewParamsByTechCard(self,data: TechCardData)->None:
        #self.repo.findParamsByCurentParam(data)
        return

    def setData(self,data: TechCardData)->None:
        pass

    def getObjectControl(self)->TechCardData:
        techCars= self.repo.get_all_controlled_element_types()
        return techCars
    
    def getControlElements(self,id)->TechCardData:
        return self.repo.get_all_objects_by_type_id(id)
    
    def getControlElementParam(self,id)->TechCardData:
        techCars= self.repo.get_params_for_type(id)
        self.pipeLine.process(techCars,0)
        return techCars
    
    def getControlElementParamValue(self,idCntlEl,idParam)->TechCardData:

        return self.repo.get_all_possible_values_by_param_and_element(idCntlEl,idParam)

    def geElementParamsValue(self,id)->TechCardData:
        techCars=self.repo.get_params_for_element(id)

        self.pipeLine.process(techCars,0)
        return techCars
    

    def updateTechCard(self,techCard)->TechCardData:
        self.pipeLine.process(techCard,0)
        return techCard