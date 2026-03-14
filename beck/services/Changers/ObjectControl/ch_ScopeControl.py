
from services.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

class ScopeControl(IDataChanger):#TODO ПНАЭ Г-7-010-89
    def changeData(self,data:TechCardData):
        if(data.hasSpecParam("Объект контроля","Объем контроля")):
            return
        param={
                "name":"Объем контроля",
                "val": ['100','50','25','10'],
                }
        data.insert_param_to_block_reWrite("Объект контроля",6,param)
             
        return