"""Тесты TechCardService с подставным репозиторием."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from repositories.Interfaces.i_repository import IRepository
from services.tech_card import TechCardData
from services.tech_card_service import TechCardService


@pytest.fixture
def mock_repos() -> MagicMock:
    r = MagicMock(spec=IRepository)
    r.get_operation_params_by_list_id.return_value = []
    r.save_tech_card_snapshot.return_value = {"id": 1, "name": "n"}
    r.list_saved_tech_cards.return_value = []
    r.get_saved_tech_card.return_value = None
    return r


def test_get_template_runs_pipeline(mock_repos, pipeline_noop):
    svc = TechCardService(mock_repos, pipeline_noop)
    card = svc.get_template()
    assert isinstance(card, TechCardData)
    assert card.has_block("ИСХОДНЫЕ ДАННЫЕ")
    assert card.has_block("ПЕРЕЧЕНЬ ОПЕРАЦИЙ РК")
    mock_repos.get_operation_params_by_list_id.assert_called()


def test_update_tech_card_delegates_to_pipeline(mock_repos, pipeline_noop):
    svc = TechCardService(mock_repos, pipeline_noop)
    card = TechCardData()
    card.set("1", {"name": "Тест", "params": {}})
    out = svc.updateTechCard(card)
    assert out is card


def test_save_tech_card_normalizes_empty_name(mock_repos, pipeline_noop):
    svc = TechCardService(mock_repos, pipeline_noop)
    svc.saveTechCard("", {"cardName": " Имя из карты "})
    mock_repos.save_tech_card_snapshot.assert_called_once()
    args = mock_repos.save_tech_card_snapshot.call_args[0]
    assert args[0] == "Имя из карты"


def test_save_tech_card_passes_card_id(mock_repos, pipeline_noop):
    svc = TechCardService(mock_repos, pipeline_noop)
    svc.saveTechCard("n", {"x": 1}, card_id=42)
    mock_repos.save_tech_card_snapshot.assert_called_once_with("n", {"x": 1}, 42)


def test_apply_operations_from_db_inserts_rows(mock_repos, pipeline_noop):
    mock_repos.get_operation_params_by_list_id.return_value = [
        {"id": 10, "name_param": "Оп А", "val": "1", "val2": None},
        {"id": 11, "name_param": "Оп Б", "val": None, "val2": "2"},
    ]
    svc = TechCardService(mock_repos, pipeline_noop)
    card = svc.crateTemplateTechCars()
    block = card.get("4")
    params = block.get("params", {})
    names = {p["name"] for p in params.values()}
    assert "Оп А" in names
    assert "Оп Б" in names


def test_list_and_get_saved_delegate(mock_repos, pipeline_noop):
    mock_repos.list_saved_tech_cards.return_value = [{"id": 1}]
    mock_repos.get_saved_tech_card.return_value = {"id": 1, "name": "x"}
    svc = TechCardService(mock_repos, pipeline_noop)
    assert svc.listSavedTechCards() == [{"id": 1}]
    assert svc.getSavedTechCard(1)["name"] == "x"
