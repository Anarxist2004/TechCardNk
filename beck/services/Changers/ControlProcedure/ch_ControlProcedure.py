from services.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

class ControlProcedure(IDataChanger):
    def changeData(self,data:TechCardData):
        if not data.hasSpecParam("Порядок проведения контроля","!Разместить"):
            param={
                    "name":"!Разместить",
                    "val": """Разметить несмываемым маркером границы контролируемых участков, их номера и
                    направление просвечивания.
                    Разметку сварного соединения на участки выполнить от точки начала отсчета.
                    Система разметки и маркировки контролируемых участков (начало и направление нумерации)
                    должна обеспечивать возможность восстановления маркировки """,
                    }    
            data.insert_param_to_block("Порядок проведения контроля",1,param)

        # if not data.hasSpecParam("Порядок проведения контроля","Разместить"):
        #     param={
        #             "name":"Cпособ сварки",
        #             "val": ['РДС','РАДС','РДС, РАДС'],
        #             }    
        #     data.insert_param_to_block("Порядок проведения контроля",2,param)

        # if not data.hasSpecParam("Порядок проведения контроля","Разместить"):
        #     param={
        #             "name":"Cпособ сварки",
        #             "val": ['РДС','РАДС','РДС, РАДС'],
        #             }    
        #     data.insert_param_to_block("Порядок проведения контроля",3,param)

        # if not data.hasSpecParam("Порядок проведения контроля","Разместить"):
        #     param={
        #             "name":"Cпособ сварки",
        #             "val": ['РДС','РАДС','РДС, РАДС'],
        #             }    
        #     data.insert_param_to_block("Порядок проведения контроля",4,param)

        # if not data.hasSpecParam("Порядок проведения контроля","Разместить"):
        #     param={
        #             "name":"Cпособ сварки",
        #             "val": ['РДС','РАДС','РДС, РАДС'],
        #             }    
        #     data.insert_param_to_block("Порядок проведения контроля",5,param)

        # if not data.hasSpecParam("Порядок проведения контроля","Разместить"):
        #     param={
        #             "name":"Cпособ сварки",
        #             "val": ['РДС','РАДС','РДС, РАДС'],
        #             }    
        #     data.insert_param_to_block("Порядок проведения контроля",6,param)

        # if not data.hasSpecParam("Порядок проведения контроля","Разместить"):
        #     param={
        #             "name":"Cпособ сварки",
        #             "val": ['РДС','РАДС','РДС, РАДС'],
        #             }    
        #     data.insert_param_to_block("Порядок проведения контроля",7,param)

        # if not data.hasSpecParam("Порядок проведения контроля","Разместить"):
        #     param={
        #             "name":"Cпособ сварки",
        #             "val": ['РДС','РАДС','РДС, РАДС'],
        #             }    
        #     data.insert_param_to_block("Порядок проведения контроля",8,param)

        # if not data.hasSpecParam("Порядок проведения контроля","Разместить"):
        #     param={
        #             "name":"Cпособ сварки",
        #             "val": ['РДС','РАДС','РДС, РАДС'],
        #             }    
        #     data.insert_param_to_block("Порядок проведения контроля",9,param)

        # if not data.hasSpecParam("Порядок проведения контроля","Разместить"):
        #     param={
        #             "name":"Cпособ сварки",
        #             "val": ['РДС','РАДС','РДС, РАДС'],
        #             }    
        #     data.insert_param_to_block("Порядок проведения контроля",10,param)
        
       
             
        return