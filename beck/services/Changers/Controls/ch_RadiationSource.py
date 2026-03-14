from services.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

class RadiationSource(IDataChanger):
    def changeData(self,data:TechCardData):

        if not data.hasSpecParam("Средства контроля","Источник излучения"):
            param={
                    "name":"Источник излучения",
                    "val": ['Гаммарид 192/120 или аналог','аналог'],#!
                    }    
            data.insert_param_to_block("Средства контроля",1,param)
        else:
            #тут задем данные
            if not data.hasSpecParam("Средства контроля","Размер фокусного пятна"):
                param={
                        "name":"Размер фокусного пятна",
                        "val": """Гаммарид 192/120 или аналог""",#!
                        }    
                data.insert_param_to_block("Средства контроля",1,param)