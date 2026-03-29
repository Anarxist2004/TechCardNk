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


class ParamsByWeldedJointFromDb(IDataChanger[TechCardData]):
    """
    Блок «Объект контроля»: для одиночного выбора «Тип сварного соединения»
    добавляет параметры из params_by_type_welding_joint: поля name, subtitle (рядом с name), val.
    Уже существующие в блоке параметры с тем же именем не дублируются.
    """

    BLOCK_OBJECT = "Объект контроля"
    PARAM_JOINT = "Тип сварного соединения"

    def __init__(self, db: IParamsByTypeWeldingJointDB):
        self._db = db

    def changeData(self, data: TechCardData) -> TechCardData:
        if not data.has_block(self.BLOCK_OBJECT):
            return data
        if not data.has_block_and_param(self.BLOCK_OBJECT, self.PARAM_JOINT):
            return data

        joint_val = data.get_param_value(self.BLOCK_OBJECT, self.PARAM_JOINT)
        if not is_scalar_choice(joint_val):
            return data

        rows = self._db.get_params_by_welded_joint_type(joint_val)
        if not rows:
            return data

        for row in rows:
            pname = row.get("name")
            if not pname or not str(pname).strip():
                continue
            pname = str(pname).strip()
            if data.has_block_and_param(self.BLOCK_OBJECT, pname):
                continue
            param = {
                "name": pname,
                "subtitle": _subtitle_value(row),
                "val": None,
            }
            data.add_param_to_block(self.BLOCK_OBJECT, param)
        return data
