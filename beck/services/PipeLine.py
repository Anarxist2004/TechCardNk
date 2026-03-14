
from services.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

class PipeLine:
    def __init__(self):
        self.changerArr = []

    def addChanger(self,changer:IDataChanger,index:int ):
        if index < 0:
            raise IndexError("index must be >= 0")
        
        if(len(self.changerArr)>index):
            self.changerArr[index].append(changer)
        elif(len(self.changerArr)==index):
            self.changerArr.append([])
            self.changerArr[index].append(changer)

    def process(self, techCard: TechCardData, index: int):
        try:
            if len(self.changerArr) < index:
                raise IndexError("index must be >= 0")
            
            for changer in self.changerArr[index]:
                changer.changeData(techCard)
            
            techCard.sort_all_params()
            
        except IndexError as e:
            # Обработка ошибки выхода за пределы массива
            print(f"Index error in process method: {e}")
            # Можно добавить логирование или другую обработку
            raise  # Если нужно пробросить исключение дальше
            
        except Exception as e:
            # Обработка других исключений
            print(f"Error in process method: {e}")
            # Дополнительная обработка или логирование
            raise  # Если нужно пробросить исключение дальше




        
