"""Тесты changer'а таблицы валиков по толщине (без БД)."""

from __future__ import annotations

import pytest

from services.Changers.ch_CircButtWeldBeadFromThicknessTable import (
    CircButtWeldBeadFromThicknessTable,
    JOINT_TYPE_CIRC,
    JOINT_TYPE_SHEET,
    PARAM_BEAD_H1,
    PARAM_BEAD_H2,
    PARAM_SHEET_E,
    PARAM_SHEET_G,
    PARAM_JOINT,
    PARAM_THICKNESS,
    BLOCK_OBJECT,
    _lookup_e_g,
    _parse_s_mm,
)
from services.tech_card import TechCardData


@pytest.mark.parametrize(
    "raw,expected",
    [
        (5, 5.0),
        ("5", 5.0),
        ("5,5", 5.5),
        (None, None),
        ("", None),
        (True, None),
    ],
)
def test_parse_s_mm(raw, expected):
    assert _parse_s_mm(raw) == expected


def test_lookup_e_g_known_range():
    assert _lookup_e_g(5) == (10, 1.5)
    assert _lookup_e_g(100) is None


def _make_object_block(**param_vals) -> TechCardData:
    card = TechCardData()
    params = {}
    i = 1
    for name, val in param_vals.items():
        params[i] = {"name": name, "val": val}
        i += 1
    card.set("ob", {"name": BLOCK_OBJECT, "params": params})
    return card


def test_circ_butt_fills_a_h1_h2():
    ch = CircButtWeldBeadFromThicknessTable()
    card = _make_object_block(
        **{
            PARAM_JOINT: JOINT_TYPE_CIRC,
            PARAM_THICKNESS: 5,
            "Ширина верхнего валика, A, мм": None,
            PARAM_BEAD_H1: None,
            PARAM_BEAD_H2: None,
        }
    )
    ch.changeData(card)
    assert card.get_param_value(BLOCK_OBJECT, "Ширина верхнего валика, A, мм") == "10"
    assert card.get_param_value(BLOCK_OBJECT, PARAM_BEAD_H1) == "1.5"
    assert card.get_param_value(BLOCK_OBJECT, PARAM_BEAD_H2) == "1.5"


def test_sheet_fills_e_g():
    ch = CircButtWeldBeadFromThicknessTable()
    card = _make_object_block(
        **{
            PARAM_JOINT: JOINT_TYPE_SHEET,
            PARAM_THICKNESS: 5,
            PARAM_SHEET_E: None,
            PARAM_SHEET_G: None,
        }
    )
    ch.changeData(card)
    assert card.get_param_value(BLOCK_OBJECT, PARAM_SHEET_E) == "10"
    assert card.get_param_value(BLOCK_OBJECT, PARAM_SHEET_G) == "1.5"


def test_no_op_when_joint_not_selected():
    ch = CircButtWeldBeadFromThicknessTable()
    card = _make_object_block(**{PARAM_JOINT: ["a", "b"], PARAM_THICKNESS: 5})
    ch.changeData(card)
    assert card.get_param_value(BLOCK_OBJECT, PARAM_THICKNESS) == 5
