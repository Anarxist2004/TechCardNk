from services.i_dataChanger import IDataChanger
from services.tech_card import TechCardData
import base64
import os

class ControlElement(IDataChanger):
    def changeData(self,data:TechCardData):
        param={
                "name":"Контролируемый элемент",
                "val": ["Сварное соединение","Стыковое сварное соединение",'Угловое сварное соединение',"Тавровое сварное соединение","Нахлесточное сварное соединение",'Кольцевое сварное соединение'],   
        }
        param2={
            "name":"картинка блок1",
            'image':'йй'
        }
        if(data.type=="пластина"):
            param={
                "name":"Контролируемый элемент",
                "val": ["Сварное соединение","Стыковое сварное соединение",'Угловое сварное соединение',"Тавровое сварное соединение","Нахлесточное сварное соединение" ],
            }
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(script_dir, '../../image/image.png')

            with open(image_path, "rb") as f:
                image_bytes = f.read()

            param2['image']=base64.b64encode(image_bytes).decode('utf-8')
        elif (data.type=="труба"):
            param={
                "name":"Контролируемый элемент",
                "val": ["Сварное соединение","Стыковое сварное соединение",'Кольцевое сварное соединение'],
        }
        data.insert_param_to_block("Объект контроля",2,param)
        data.insert_param_to_block("Объект контроля",10,param2)
        
       


        # for block_key, block in data["params"].items():
        #     if block.get("name") == "Объект контроля":
        # # добавляем новый параметр
        #         next_param_key = str(len(block["params"]) + 1)  # автоматически следующий ключ
        #         block["params"][next_param_key] = {"name": "Язык реализации", "val": "Python"}
        #         print(f'Параметр добавлен в блок "{block_key}"')
        #     break
        # else:
        #     print("Блок с именем 'Объект контроля' не найден")
        return