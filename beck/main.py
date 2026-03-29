import io
import sys
from repositories.postgresDataBase import PostgresDataBase
from controllers.adapterWeb import create_adapter
from controllers.controllerWeb import ControllerWeb
from services.PipeLine import PipeLine
from services.tech_card_service import TechCardService
from services.Changers.ch_ControlMethodsFromDb import ControlMethodsFromDb
from services.Changers.ch_RegulatoryDocumentsFromDb import RegulatoryDocumentsFromDb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DB_DSN = "host=localhost port=5435 dbname=victor user=postgres password=1"


def create_pipeline(repos: PostgresDataBase) -> PipeLine:
    pipe_line = PipeLine()
    pipe_line.addChanger(ControlMethodsFromDb(repos), 0)
    pipe_line.addChanger(RegulatoryDocumentsFromDb(repos), 0)
    return pipe_line


def main():
    repos = PostgresDataBase(DB_DSN)
    service = TechCardService(repos, create_pipeline(repos))
    controller = ControllerWeb(service)
    create_adapter(controller)


if __name__ == "__main__":
    main()
