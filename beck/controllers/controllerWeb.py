from controllers.Interfaces.i_controllers import IControllers
from services.tech_card import TechCardData
from services.Interfaces.i_servise import IServise

class ControllerWeb(IControllers[TechCardData]):
    def __init__(self,serv:IServise):
        self.serv=serv   
        return

    def get_template(self):
        techCard=self.serv.get_template()
        return techCard.serialise()
    
    def updateTechCard(self,techCard)->TechCardData:##обновляем тех карту
        data =TechCardData()
        data.from_jsonDeSerialise(techCard)
        return self.serv.updateTechCard(data)
