from services.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

class SetReadOnlyTrueSourceData(IDataChanger):
    def changeData(self, data: TechCardData):
        """
        Устанавливает readonly=False для всех параметров в блоке 'ИСХОДНЫЕ ДАННЫЕ'
        """
        # Находим блок 'ИСХОДНЫЕ ДАННЫЕ'
        for block in data.params.values():
            if block.get("name") == "ИСХОДНЫЕ ДАННЫЕ":
                params = block.get("params", {})
                
                # Проходим по всем параметрам блока
                for param in params.values():
                    if isinstance(param, dict) and "readOnly" in param:
                        param["readOnly"] = False
                
                break  # блок найден и обработан, выходим из цикла
        
        return data