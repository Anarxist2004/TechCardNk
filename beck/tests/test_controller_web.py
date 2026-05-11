"""Тесты ControllerWeb с подставным сервисом."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from controllers.controllerWeb import ControllerWeb
from services.Interfaces.i_servise import IServise
from services.tech_card import TechCardData


@pytest.fixture
def mock_service() -> MagicMock:
    s = MagicMock(spec=IServise)
    return s


def test_get_template_returns_serialised_json_string(mock_service):
    card = TechCardData()
    card.set("1", {"name": "H", "params": {}})
    mock_service.get_template.return_value = card
    ctrl = ControllerWeb(mock_service)
    out = ctrl.get_template()
    assert isinstance(out, str)
    assert json.loads(out)["params"]["1"]["name"] == "H"


def test_update_tech_card_deserialises_and_calls_service(mock_service):
    def _proc(data):
        data.set("1", {"name": "Y", "params": {}})
        return data

    mock_service.updateTechCard.side_effect = _proc
    ctrl = ControllerWeb(mock_service)
    payload = {"params": {"1": {"name": "X", "params": {}}}}
    result = ctrl.updateTechCard(payload)
    assert isinstance(result, TechCardData)
    mock_service.updateTechCard.assert_called_once()


def test_save_list_get_delegate(mock_service):
    mock_service.saveTechCard.return_value = {"id": 1}
    mock_service.listSavedTechCards.return_value = []
    mock_service.getSavedTechCard.return_value = None
    ctrl = ControllerWeb(mock_service)
    assert ctrl.saveTechCard("n", {}) == {"id": 1}
    assert ctrl.listSavedTechCards() == []
    assert ctrl.getSavedTechCard(0) is None
