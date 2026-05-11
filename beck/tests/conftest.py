"""
Общие фикстуры pytest.
"""

from __future__ import annotations

import pytest

from controllers.controllerWeb import ControllerWeb
from services.Interfaces.i_dataChanger import IDataChanger
from services.PipeLine import PipeLine
from services.tech_card import TechCardData
from services.tech_card_service import TechCardService


class NoOpChanger(IDataChanger[TechCardData]):
    """Changer без побочных эффектов — чтобы pipeline имел непустую фазу 0."""

    def changeData(self, data: TechCardData) -> TechCardData:
        return data


@pytest.fixture
def pipeline_noop() -> PipeLine:
    pl = PipeLine()
    pl.addChanger(NoOpChanger(), 0)
    return pl
