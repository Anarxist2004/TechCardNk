from services.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

class WeldingMethod(IDataChanger):
    def changeData(self,data:TechCardData):
        if(data.hasSpecParam("Объект контроля","Cпособ сварки")):
            return
        param={
                "name":"Cпособ сварки",
                "val": ['РДС','РАДС','РДС, РАДС'],
                }
        data.insert_param_to_block_reWrite("Объект контроля",'6',param)
             
        return
    
