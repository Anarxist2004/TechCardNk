from services.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

class SetSortament(IDataChanger):
    def changeData(self,data:TechCardData):

        data.change_param_id_by_name_autoshift("Объект контроля","Размеры контролируемых элементов",'4')
        

        if(data.change_param_id_by_name_autoshift("Объект контроля","Расчетная высота углового шва, h, мм",'4.2')):
            data.change_param_id_by_name_autoshift("Объект контроля","Наружный диаметр, D, мм",'4.1')
        elif(data.change_param_id_by_name_autoshift("Объект контроля","Наружный диаметр, D, мм",'4.1')):
            data.change_param_id_by_name_autoshift("Объект контроля","Толщина, S, мм",'4.2')
        else:
            data.change_param_id_by_name_autoshift("Объект контроля","Толщина, S, мм",'4.1')
        
        return