import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from repositories.postgresDataBase import PostgresDataBase
from repositories.PostgreDbShablov import PostgreDbShablov

from services.tech_card_service import TechCardService
from services.tech_card_service import TechCardData
from services.PipeLine import PipeLine
from controllers.controllerWeb import ControllerWeb
from controllers.adapterWeb import create_adapter

from services.Changers.ObjectControl.ch_CategoryPNA import CategoryPNA
from services.Changers.ObjectControl.ch_ControlElement import ControlElement
from services.Changers.ObjectControl.ch_TypeWeldedJoint import  TypeWeldedJoint
from services.Changers.ObjectControl.ch_SetSortament import SetSortament
from services.Changers.ObjectControl.ch_WidthHeightBulgeST526480 import WidthHeightBulgeST526480
from services.Changers.ObjectControl.ch_WeldingMethod import WeldingMethod
from services.Changers.ObjectControl.ch_ScopeControl import ScopeControl
from services.Changers.ObjectControl.ch_ControlZone import ControlZone

from services.Changers.RegulatoryMethodologicalDocumentation.ch_BlockRegMeth import BlockRegMeth

from services.Changers.ControlConditions.ch_ControlConditions import ControlConditions

from services.Changers.PreparationControl.ch_PreparationControl import PreparationControl
from services.Changers.ControlProcedure.ch_ControlProcedure import ControlProcedure

#заглушка 
from services.Changers.RegulatoryMethodologicalDocumentation.sh_Stub import Stub
def createPipeLine()->PipeLine:
    pipeLine =PipeLine()
    pipeLine.addChanger(SetSortament(),0)#2
    pipeLine.addChanger(ControlElement(),0)#2
    pipeLine.addChanger(CategoryPNA(),0)#3
    pipeLine.addChanger(TypeWeldedJoint(),0)#5
    pipeLine.addChanger(WidthHeightBulgeST526480(),0)
    pipeLine.addChanger(WeldingMethod(),0)
    pipeLine.addChanger(ScopeControl(),0)
    pipeLine.addChanger(ControlZone(),0)

    pipeLine.addChanger(BlockRegMeth(),0)

    pipeLine.addChanger(ControlConditions(),0)

    pipeLine.addChanger(PreparationControl(),0)

    # pipeLine.addChanger(ControlProcedure(),0)#6 доделать

    pipeLine.addChanger(Stub(),0)#Заглушка
    
    return pipeLine

def createPipeLineShablov()->PipeLine:
    pipeLine =PipeLine()
    return pipeLine
test =False

# def main():
#     repo = PostgresDataBase("host=localhost port=5435 dbname=techCard user=postgres password=1")
#     controller=ControllerWeb()
#     service = TechCardService(repo,createPipeLine())
#     controller.setServise(service)
#     create_adapter(controller)

    
def main():
    #repo = PostgresDataBase("host=localhost port=5435 dbname=techCard user=postgres password=1")
    repo = PostgreDbShablov("host=localhost port=5435 dbname=welding_control_db user=postgres password=1")
    controller=ControllerWeb()
    service = TechCardService(repo,createPipeLineShablov())
    controller.setServise(service)
    create_adapter(controller)    


def testF():
    repo = PostgresDataBase("host=localhost port=5432 dbname=techcard user=postgres password=admin")
#     controller=ControllerWeb()
#     controller.setServise(service)
#     #create_adapter(controller)

#     # tech_data3 = TechCardData({
#     #     "typeOfControlledlement": 0,  
#     # })
#     print(repo.get_all_possible_values_by_param_and_element(1,2 ))
#    # print(repo.get_all_controlled_element_types())
#     #print(service.findNewParamsByTechCard(tech_data3))
#     #print(tech_data3)
#     a=0
#     a+=1
    
if __name__ == "__main__":
    if(test):
        testF()
    else: 
        main()