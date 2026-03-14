from services.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

class ShablovObjectControl(IDataChanger):
    def changeData(self,data:TechCardData):

        if not (data.hasSpecParam("Объект контроля","Предприятие-изготовитель")):
            param={
                "name":"Предприятие-изготовитель",
                "val": 'ООО "Технология"',
                }
            data.insert_param_to_block_reWrite("Предприятие-изготовитель",1,param)
  
        return