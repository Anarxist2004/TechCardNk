from services.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

class ControlZone(IDataChanger):
    def changeData(self,data:TechCardData):
        if(data.hasSpecParam("Объект контроля","Зона контроля")):
            return
        param={
                "name":"Зона контроля",
                "val": [],
                }
        
        s=None
        if(data.hasSpecParam("Объект контроля","Толщина, S, мм")):
            s=data.get_param_value("Объект контроля","Толщина, S, мм")
        else:
            data.insert_param_to_block_reWrite("Объект контроля",9,param)
            return

        
        if(s<=5):
            param['val']="не менее 5"
        if(s<=20):
            param['val']="не менее "+str(s)
        elif(s>20):
            param['val']="не менее 20"
        
        data.insert_param_to_block_reWrite("Объект контроля",9,param)
             
        return