from services.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

class WidthHeightBulgeST526480(IDataChanger):
    def changeData(self,data:TechCardData):

        if(data.hasSpecParam("Объект контроля","Тип сварного соединения")==False):
            return
        if(data.hasSpecParam("Объект контроля","Толщина, S, мм")==False):
            return
        s= data.get_param_value("Объект контроля","Толщина, S, мм")
        val=data.get_param_value("Объект контроля","Тип сварного соединения") 
        
        width=0
        height=0    

        if('С17' or 'C17' in val):
            tp=self.C17Calc(s)
            width=tp[0]
            height=tp[1]

        param={
            'name': 'Ширина выпуклости усиления, е, мм',
            'val':width,
        }
        data.insert_param_to_block_reWrite("Объект контроля",'4.2',param)  
        param={
            'name': 'Высота выпуклости сварного шва',
            'val':height,
        }  
        data.insert_param_to_block_reWrite("Объект контроля",'4.3',param)    

        return
    
    def C17Calc(self,s)->tuple:
        e=0
        S = int(s)
        if 3 <= S <= 5:
            e= '8'
        elif 5 < S <= 8:
            e= '12'
        elif 8 < S <= 11:
            e= '16'
        elif 11 < S <= 14:
            e= '19'
        elif 14 < S <= 17:
            e= '22'
        elif 17 < S <= 20:
            e= '26'
        elif 20 < S <= 24:
            e= '30'
        elif 24 < S <= 28:
            e= '34'
        elif 28 < S <= 32:
            e= '38'
        elif 32 < S <= 36:
            e= '42'
        elif 36 < S <= 40:
            e= '47'
        elif 40 < S <= 44:
            e= '52'
        elif 44 < S <= 48:
            e= '54'
        elif 48 < S <= 52:
            e= '56'
        elif 52 < S <= 56:
            e= '60'
        elif 56 < S <= 60:
            e= '65'

        dif=0
        if(S<=14):
            dif='+-2'
        elif(S<=40):
            dif='+-3'
        elif(S<=60):
             dif='+-4'

        e+=dif

        g='0.5'
        if(S<=14):
            g+='+1.5-1.5'
        else:
            g+='+2-0.5'

        return e,g

