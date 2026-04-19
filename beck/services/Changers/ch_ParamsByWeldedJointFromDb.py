from typing import Any, Dict, Set

from services.Interfaces.i_dataChanger import IDataChanger
from repositories.Interfaces.i_params_by_type_welding_joint_db import (
    IParamsByTypeWeldingJointDB,
)
from services.tech_card import TechCardData
from services.Changers.param_choice import is_scalar_choice


def _subtitle_value(row: dict):
    raw = row.get("subtitle")
    if raw is None:
        return None
    if isinstance(raw, str):
        s = raw.strip()
        return s if s else None
    return str(raw)


_PARAM_FROM_JOINT_DB = "from_welded_joint_params_db"
_PARAM_JOINT_BINDING = "welded_joint_binding"


class ParamsByWeldedJointFromDb(IDataChanger[TechCardData]):
    """
    Блок «Объект контроля»: параметры из params_by_type_welding_joint для выбранного
    «Тип сварного соединения» помечаются from_welded_joint_params_db.

    Синхронизация:
    1) имена параметров на карте с флагом;
    2) имена параметров из БД для текущего типа шва;
    только в (1) — удаляем;
    для каждого имени из (2): если поле уже есть на карте — вешаем флаг и binding,
    обновляем subtitle, val не меняем; иначе добавляем параметр с val=null.
    """

    BLOCK_OBJECT = "Объект контроля"
    PARAM_JOINT = "Тип сварного соединения"
    _PROTECTED_NAMES = frozenset({PARAM_JOINT, "Схема"})

    def __init__(self, db: IParamsByTypeWeldingJointDB):
        self._db = db

    def _iter_object_control_params(self, data: TechCardData):
        for block in data.params.values():
            if block.get("name") != self.BLOCK_OBJECT:
                continue
            params = block.get("params") or {}
            for p in params.values():
                if isinstance(p, dict):
                    yield p

    def _flagged_param_names(self, data: TechCardData) -> Set[str]:
        """Имена параметров на карте с флагом from_welded_joint_params_db."""
        out: Set[str] = set()
        for p in self._iter_object_control_params(data):
            if p.get(_PARAM_FROM_JOINT_DB) is not True:
                continue
            pname = str(p.get("name") or "").strip()
            if pname and pname not in self._PROTECTED_NAMES:
                out.add(pname)
        return out

    def _db_param_names(self, rows: list) -> Set[str]:
        out: Set[str] = set()
        for row in rows or []:
            pname = row.get("name")
            if pname and str(pname).strip():
                out.add(str(pname).strip())
        return out

    def _meta_for_row(self, joint_val: Any) -> dict:
        return {
            _PARAM_FROM_JOINT_DB: True,
            _PARAM_JOINT_BINDING: joint_val,
        }

    def changeData(self, data: TechCardData) -> TechCardData:
        if not data.has_block(self.BLOCK_OBJECT):
            return data
        if not data.has_block_and_param(self.BLOCK_OBJECT, self.PARAM_JOINT):
            return data

        joint_val = data.get_param_value(self.BLOCK_OBJECT, self.PARAM_JOINT)
        if not is_scalar_choice(joint_val):
            return data

        rows = self._db.get_params_by_welded_joint_type(joint_val) or []
        on_card_flagged = self._flagged_param_names(data)
        from_db = self._db_param_names(rows)

        for pname in on_card_flagged - from_db:
            while data.has_block_and_param(self.BLOCK_OBJECT, pname):
                data.remove_param_from_block(self.BLOCK_OBJECT, pname)

        meta = self._meta_for_row(joint_val)
        for row in rows:
            pname = row.get("name")
            if not pname or not str(pname).strip():
                continue
            pname = str(pname).strip()
            if pname in self._PROTECTED_NAMES:
                continue
            subtitle = _subtitle_value(row)
            fields: Dict[str, Any] = {**meta}
            if subtitle is not None:
                fields["subtitle"] = subtitle
            if data.has_block_and_param(self.BLOCK_OBJECT, pname):
                data.update_param(self.BLOCK_OBJECT, pname, fields)
                continue
            param = {
                "name": pname,
                "subtitle": subtitle,
                "val": None,
                **meta,
            }
            data.add_param_to_block(self.BLOCK_OBJECT, param)

        return data
