import io
import sys

from controllers.adapterWeb import create_adapter
from controllers.controllerWeb import ControllerWeb
from repositories.PostgreDbShablovGazprom import PostgreDbShablovGazprom
from repositories.PostgreDbShablovGazpromOperational import PostgreDbShablovGazpromOperational
from services.Changers.Gazprom.ch_ExpandJsonPayloads import ExpandJsonPayloads
from services.PipeLine import PipeLine
from services.tech_card_service import TechCardService

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DB_DSN = "host=localhost port=5432 dbname=welding_control_db user=postgres password=admin"


def fill_gazprom_pipeline(pipe_line: PipeLine) -> None:
    methodology_id = TechCardService.GAZPROM_METHODOLOGY
    pipe_line.addChanger(ExpandJsonPayloads(), methodology_id)


def fill_gazprom_operational_pipeline(pipe_line: PipeLine) -> None:
    methodology_id = TechCardService.GAZPROM_OPERATIONAL_METHODOLOGY
    pipe_line.addChanger(ExpandJsonPayloads(), methodology_id)


def create_pipeline() -> PipeLine:
    pipe_line = PipeLine()
    fill_gazprom_pipeline(pipe_line)
    fill_gazprom_operational_pipeline(pipe_line)
    return pipe_line


def main():
    repos = {
        TechCardService.GAZPROM_METHODOLOGY: PostgreDbShablovGazprom(
            DB_DSN
        ),
        TechCardService.GAZPROM_OPERATIONAL_METHODOLOGY: PostgreDbShablovGazpromOperational(
            DB_DSN
        ),
    }
    controller = ControllerWeb()
    service = TechCardService(repos, create_pipeline())
    controller.setServise(service)
    create_adapter(controller)


if __name__ == "__main__":
    main()
