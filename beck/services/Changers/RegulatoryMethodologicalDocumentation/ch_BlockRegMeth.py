from services.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

class BlockRegMeth(IDataChanger):
    def changeData(self,data:TechCardData):
        if not (data.hasSpecParam("Нормативная и методическая документация","Нормативная")):
            param={
                "name":"Нормативная",
                "val": 'ПНАЭ Г-7- 010-89',
                }
            data.insert_param_to_block_reWrite("Нормативная и методическая документация",1,param)
        if not (data.hasSpecParam("Нормативная и методическая документация","методическая ")):
            param={
                "name":"Методическая",
                "val": 'ПНАЭ Г-7- 017-89 ; ГОСТ 7512-82',
                }
            data.insert_param_to_block_reWrite("Нормативная и методическая документация",2,param)
       
             
        return