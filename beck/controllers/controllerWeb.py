from interfaces.i_controllers import IControllers
from services.tech_card import TechCardData
from interfaces.i_servise import IServise

class ControllerWeb(IControllers[TechCardData]):
    def __init__(self):
        pass

    def setServise(self,serv:IServise):
        self.serv=serv    
    
    def getObjectControl(self, methodology=0)->TechCardData:
        return self.serv.getObjectControl(methodology)
    
    def getControlElements(self,id, methodology=0)->TechCardData:
        return self.serv.getControlElements(id, methodology)
    
    def getControlElementParam(self,id, methodology=0)->TechCardData:
        return self.serv.getControlElementParam(id, methodology)
    
    def getControlElementParamValue(self,idCntlEl,idParam)->TechCardData:
        return self.serv.getControlElementParamValue(idCntlEl,idParam)

    def getElementParamsValues(self,idCntEl, methodology=0)->TechCardData:
        return self.serv.geElementParamsValue(idCntEl, methodology)        
    
    def handle_request(self, data: TechCardData) -> TechCardData:
        """Обрабатывает входные данные и возвращает результат"""
        pass

    def updateTechCard(self,techCard)->TechCardData:##обновляем тех карту
        data =TechCardData()
        data.from_jsonDeSerialise(techCard)
        return self.serv.updateTechCard(data)

    def getMethodologies(self):
        return self.serv.getMethodologies()
