import io
import sys
from repositories.postgresDataBase import PostgresDataBase
from controllers.adapterWeb import create_adapter
from controllers.controllerWeb import ControllerWeb
from services.PipeLine import PipeLine
from services.tech_card_service import TechCardService
from services.Changers.ch_ControlMethodsFromDb import ControlMethodsFromDb
from services.Changers.ch_RegulatoryDocumentsFromDb import RegulatoryDocumentsFromDb
from services.Changers.ch_TypeOfWeldedJointFromDb import TypeOfWeldedJointFromDb
from services.Changers.ch_WeldedJointDiagramFromDb import WeldedJointDiagramFromDb
from services.Changers.ch_ParamsByWeldedJointFromDb import ParamsByWeldedJointFromDb
from services.Changers.ch_ControlSchemesFromDb import ControlSchemesFromJointTypeDb
from services.Changers.ch_ControlledZoneWidthStub import ControlledZoneWidthStub
from services.Changers.ch_ControlSensitivity import ControlSensitivityChanger

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DB_DSN = "host=localhost port=5432 dbname=victor user=postgres password=admin"


def create_pipeline(repos: PostgresDataBase) -> PipeLine:
    pipe_line = PipeLine()
    pipe_line.addChanger(ControlMethodsFromDb(repos), 0)
    pipe_line.addChanger(RegulatoryDocumentsFromDb(repos), 0)
    pipe_line.addChanger(TypeOfWeldedJointFromDb(repos), 0)
    pipe_line.addChanger(WeldedJointDiagramFromDb(repos), 0)
    pipe_line.addChanger(ControlSchemesFromJointTypeDb(repos), 0)
    pipe_line.addChanger(ParamsByWeldedJointFromDb(repos), 0)
    pipe_line.addChanger(ControlSensitivityChanger(), 0)
    pipe_line.addChanger(ControlledZoneWidthStub(), 0)
    return pipe_line


def main():
    repos = PostgresDataBase(DB_DSN)
    service = TechCardService(repos, create_pipeline(repos))
    controller = ControllerWeb(service)
    create_adapter(controller)


if __name__ == "__main__":
    main()
