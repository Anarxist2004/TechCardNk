import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from repositories.postgresDataBase import PostgresDataBase
from repositories.PostgreDbShablovGazprom import PostgreDbShablovGazprom

from services.tech_card_service import TechCardService
from services.tech_card import TechCardData
from services.PipeLine import PipeLine
from controllers.controllerWeb import ControllerWeb
from controllers.adapterWeb import create_adapter

from services.Changers.ObjectControl.ch_CategoryPNA import CategoryPNA
from services.Changers.ObjectControl.ch_ControlElement import ControlElement
from services.Changers.ObjectControl.ch_TypeWeldedJoint import TypeWeldedJoint
from services.Changers.ObjectControl.ch_SetSortament import SetSortament
from services.Changers.ObjectControl.ch_WidthHeightBulgeST526480 import WidthHeightBulgeST526480
from services.Changers.ObjectControl.ch_WeldingMethod import WeldingMethod
from services.Changers.ObjectControl.ch_ScopeControl import ScopeControl
from services.Changers.ObjectControl.ch_ControlZone import ControlZone

from services.Changers.RegulatoryMethodologicalDocumentation.ch_BlockRegMeth import BlockRegMeth

from services.Changers.ControlConditions.ch_ControlConditions import ControlConditions

from services.Changers.PreparationControl.ch_PreparationControl import PreparationControl
from services.Changers.ControlProcedure.ch_ControlProcedure import ControlProcedure

from services.Changers.RegulatoryMethodologicalDocumentation.sh_Stub import Stub
from services.Changers.Gazprom.ch_ExpandJsonPayloads import ExpandJsonPayloads


def fillRosatomPipeLine(pipeLine: PipeLine) -> None:
    methodology_id = TechCardService.ROSATOM_METHODOLOGY
    pipeLine.addChanger(SetSortament(), methodology_id)
    pipeLine.addChanger(ControlElement(), methodology_id)
    pipeLine.addChanger(CategoryPNA(), methodology_id)
    pipeLine.addChanger(TypeWeldedJoint(), methodology_id)
    pipeLine.addChanger(WidthHeightBulgeST526480(), methodology_id)
    pipeLine.addChanger(WeldingMethod(), methodology_id)
    pipeLine.addChanger(ScopeControl(), methodology_id)
    pipeLine.addChanger(ControlZone(), methodology_id)
    pipeLine.addChanger(BlockRegMeth(), methodology_id)
    pipeLine.addChanger(ControlConditions(), methodology_id)
    pipeLine.addChanger(PreparationControl(), methodology_id)
    # pipeLine.addChanger(ControlProcedure(), methodology_id)  # доделать
    pipeLine.addChanger(Stub(), methodology_id)


def fillGazpromPipeLine(pipeLine: PipeLine) -> None:
    methodology_id = TechCardService.GAZPROM_METHODOLOGY
    pipeLine.addChanger(ExpandJsonPayloads(), methodology_id)


def createPipeLine() -> PipeLine:
    pipeLine = PipeLine()
    fillRosatomPipeLine(pipeLine)
    fillGazpromPipeLine(pipeLine)
    return pipeLine


test = False


def main():
    repos = {
        TechCardService.ROSATOM_METHODOLOGY: PostgresDataBase(
            "host=localhost port=5432 dbname=techCard user=postgres password=admin"
        ),
        TechCardService.GAZPROM_METHODOLOGY: PostgreDbShablovGazprom(
            "host=localhost port=5432 dbname=welding_control_db user=postgres password=admin"
        ),
    }
    controller = ControllerWeb()
    service = TechCardService(repos, createPipeLine())
    controller.setServise(service)
    create_adapter(controller)

# def main():
#     repos = {
#         TechCardService.ROSATOM_METHODOLOGY: PostgresDataBase(
#             "host=localhost port=5435 dbname=techCard user=postgres password=1"
#         ),
#         TechCardService.GAZPROM_METHODOLOGY: PostgreDbShablovGazprom(
#             "host=localhost port=5435 dbname=welding_control_db user=postgres password=1"
#         ),
#     }
#     controller = ControllerWeb()
#     service = TechCardService(repos, createPipeLine())
#     controller.setServise(service)
#     create_adapter(controller)

if __name__ == "__main__":
        main()
