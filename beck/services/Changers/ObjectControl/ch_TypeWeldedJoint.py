

from services.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

class TypeWeldedJoint(IDataChanger):
    def changeData(self,data:TechCardData):
        if(data.hasSpecParam("Объект контроля","Тип сварного соединения")):
            return
        param={
                "name":"Тип сварного соединения",
                "val": ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'C27', 'C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C34', 'C35', 'C36', 'C37', 'C38', 'C39', 'C40', 'C41', 'C42', 'C43', 'C44', 'C45','У1', 'У2', 'У3', 'У4', 'У5', 'У6', 'У7', 'У8', 'У9', 'У10', 'У11','Т1', 'Т2', 'Т3', 'Т4', 'Т5', 'Т6', 'Т7', 'Т8', 'Т9', 'Т10', 'Т11', 'Т12','Н1', 'Н2'],
                }
        string=data.get_param_value("Объект контроля","Контролируемый элемент")
        if isinstance(string, str):
            if"Стыковое сварное соединение" in string:
                param["val"]=['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'C27', 'C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C34', 'C35', 'C36', 'C37', 'C38', 'C39', 'C40', 'C41', 'C42', 'C43', 'C44', 'C45']
            elif 'Угловое сварное соединение' in string:
                param["val"]=['У1', 'У2', 'У3', 'У4', 'У5', 'У6', 'У7', 'У8', 'У9', 'У10', 'У11']
            elif "Тавровое сварное соединение" in string:
                param["val"]=['Т1', 'Т2', 'Т3', 'Т4', 'Т5', 'Т6', 'Т7', 'Т8', 'Т9', 'Т10', 'Т11', 'Т12']
            elif "Нахлесточное сварное соединение" in string:
                param["val"]=['Н1', 'Н2']

        data.insert_param_to_block_reWrite("Объект контроля",5,param)
             
        return