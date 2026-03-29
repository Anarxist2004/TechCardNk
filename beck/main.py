import io
import sys
from repositories.postgresDataBase import PostgresDataBase
from controllers.adapterWeb import create_adapter
from controllers.controllerWeb import ControllerWeb
from services.PipeLine import PipeLine
from services.tech_card_service import TechCardService

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DB_DSN = "host=localhost port=5435 dbname=welding_control_db user=postgres password=1"

def create_pipeline() -> PipeLine:
    pipe_line = PipeLine()
    return pipe_line


def main():
    repos = PostgresDataBase(DB_DSN)
    service = TechCardService(repos, create_pipeline())
    controller = ControllerWeb(service)
    create_adapter(controller)


if __name__ == "__main__":
    main()
