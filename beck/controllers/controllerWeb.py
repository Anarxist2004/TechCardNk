from interfaces.i_controllers import IControllers
from services.tech_card import TechCardData
from interfaces.i_servise import IServise

class ControllerWeb(IControllers[TechCardData]):
    def __init__(self):
        pass

    def setServise(self,serv:IServise):
        self.serv=serv    
    
    def getObjectControl(self)->TechCardData:
        return self.serv.getObjectControl()
    
    def getControlElements(self,id)->TechCardData:
        return self.serv.getControlElements(id)
    
    def getControlElementParam(self,id)->TechCardData:
        return self.serv.getControlElementParam(id)
    
    def getControlElementParamValue(self,idCntlEl,idParam)->TechCardData:
        return self.serv.getControlElementParamValue(idCntlEl,idParam)

    def getElementParamsValues(self,idCntEl)->TechCardData:
        return self.serv.geElementParamsValue(idCntEl)        
    
    def handle_request(self, data: TechCardData) -> TechCardData:
        """Обрабатывает входные данные и возвращает результат"""
        pass

    def updateTechCard(self,techCard)->TechCardData:##обновляем тех карту
        data =TechCardData()
        data.from_jsonDeSerialise(techCard)
        return self.serv.updateTechCard(data)


