"""Тесты модели TechCardData."""

from __future__ import annotations

import json

import pytest

from services.tech_card import TechCardData


def test_serialise_is_valid_json():
    card = TechCardData()
    card.set("1", {"name": "Заголовок", "params": {}})
    raw = card.serialise()
    data = json.loads(raw)
    assert "params" in data
    assert "1" in data["params"]


def test_from_json_deserialise_dict():
    card = TechCardData()
    payload = {"type": 1, "methodology": 2, "params": {"x": {"name": "blk", "params": {}}}}
    card.from_jsonDeSerialise(payload)
    assert card.methodology == 2
    assert "x" in card.params


def test_has_block_and_param():
    card = TechCardData()
    card.set("2", {"name": "Объект контроля", "params": {1: {"name": "Поле", "val": 1}}})
    assert card.has_block("Объект контроля")
    assert card.has_block_and_param("Объект контроля", "Поле")
    assert not card.has_block_and_param("Объект контроля", "Нет такого")


def test_insert_param_to_block_shifts_ids():
    card = TechCardData()
    card.set("1", {"name": "Блок", "params": {1: {"name": "a", "val": 1}}})
    ok = card.insert_param_to_block("Блок", 1, {"name": "b", "val": 2})
    assert ok
    params = card.get("1")["params"]
    assert params[1]["name"] == "b"
    assert params[2]["name"] == "a"


def test_add_param_to_block_rejects_duplicate_name():
    card = TechCardData()
    card.set("1", {"name": "Блок", "params": {1: {"name": "x", "val": 1}}})
    assert card.add_param_to_block("Блок", {"name": "x", "val": 2}) is False
