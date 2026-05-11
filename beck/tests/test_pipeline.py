"""Тесты конвейера PipeLine."""

from __future__ import annotations

import pytest

from services.PipeLine import PipeLine
from services.Interfaces.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

from tests.conftest import NoOpChanger


class AppendMarkerChanger(IDataChanger[TechCardData]):
    def __init__(self, marker: str):
        self.marker = marker

    def changeData(self, data: TechCardData) -> TechCardData:
        data.set("_test_marker", {"name": self.marker, "params": {}})
        return data


def test_add_changer_negative_index_raises():
    pl = PipeLine()
    with pytest.raises(IndexError, match="index must be >= 0"):
        pl.addChanger(NoOpChanger(), -1)


def test_process_index_out_of_range_raises():
    pl = PipeLine()
    card = TechCardData()
    with pytest.raises(IndexError):
        pl.process(card, 0)


def test_process_runs_changers_in_order():
    pl = PipeLine()
    pl.addChanger(AppendMarkerChanger("first"), 0)
    pl.addChanger(AppendMarkerChanger("second"), 0)
    card = TechCardData()
    pl.process(card, 0)
    assert card.get("_test_marker")["name"] == "second"


def test_process_calls_sort_all_params():
    pl = PipeLine()
    pl.addChanger(NoOpChanger(), 0)
    card = TechCardData()
    card.set("1", {"name": "B", "params": {2: {"name": "p2"}, 1: {"name": "p1"}}})
    pl.process(card, 0)
    keys = list(card.get("1")["params"].keys())
    assert keys == [1, 2]
