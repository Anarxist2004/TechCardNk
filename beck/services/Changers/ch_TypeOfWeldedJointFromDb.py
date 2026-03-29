from services.Interfaces.i_dataChanger import IDataChanger
from repositories.Interfaces.i_type_of_welded_joint_db import ITypeOfWeldedJointDB
from services.tech_card import TechCardData
from services.Changers.param_choice import is_scalar_choice


def _is_empty_val(val) -> bool:
    if val is None:
        return True
    if isinstance(val, str) and not val.strip():
        return True
    if isinstance(val, (list, tuple)) and len(val) == 0:
        return True
    return False


class TypeOfWeldedJointFromDb(IDataChanger[TechCardData]):
    """
    Блок «Объект контроля»: «Тип сварного соединения» (subtitle: ОБЪЕКТ КОНТРОЛЯ).
    Подставляет данные только если «НОРМАТИВНЫЕ ДОКУМЕНТЫ» — одиночный выбор (str/int),
    не пустое и не массив.
    """

    BLOCK_OTK = (
        "ОПЕРАЦИОННАЯ ТЕХНОЛОГИЧЕСКАЯ КАРТА РАДИОГРАФИЧЕСКОГО КОНТРОЛЯ "
        "СВАРНЫХ СОЕДИНЕНИЙ"
    )
    BLOCK_OBJECT = "Объект контроля"
    PARAM_REGULATORY = "НОРМАТИВНЫЕ ДОКУМЕНТЫ"
    PARAM_JOINT = "Тип сварного соединения"
    SUBTITLE_JOINT = "ОБЪЕКТ КОНТРОЛЯ"

    def __init__(self, db: ITypeOfWeldedJointDB):
        self._db = db

    def _fetch_rows_for_regulatory(self, reg_val):
        if not is_scalar_choice(reg_val):
            return None
        if isinstance(reg_val, int):
            return self._db.get_type_of_welded_joints_by_regulatory_document_id(
                reg_val
            )
        return self._db.get_type_of_welded_joints_for_regulatory_document_name(
            reg_val.strip()
        )

    def changeData(self, data: TechCardData) -> TechCardData:
        if not data.has_block(self.BLOCK_OTK):
            return data
        if not data.has_block_and_param(self.BLOCK_OTK, self.PARAM_REGULATORY):
            return data
        if not data.has_block(self.BLOCK_OBJECT):
            return data

        if data.has_block_and_param(self.BLOCK_OBJECT, self.PARAM_JOINT):
            if not _is_empty_val(
                data.get_param_value(self.BLOCK_OBJECT, self.PARAM_JOINT)
            ):
                return data

        reg_val = data.get_param_value(self.BLOCK_OTK, self.PARAM_REGULATORY)
        if not is_scalar_choice(reg_val):
            return data

        rows = self._fetch_rows_for_regulatory(reg_val)
        if rows is None:
            return data
        if not rows:
            return data

        names = [r["name"] for r in rows if r.get("name") is not None]

        if data.has_block_and_param(self.BLOCK_OBJECT, self.PARAM_JOINT):
            data.set_param_value(self.BLOCK_OBJECT, self.PARAM_JOINT, names)
            data.update_param(
                self.BLOCK_OBJECT,
                self.PARAM_JOINT,
                {"subtitle": self.SUBTITLE_JOINT},
            )
        else:
            data.add_param_to_block(
                self.BLOCK_OBJECT,
                {
                    "name": self.PARAM_JOINT,
                    "val": names,
                    "subtitle": self.SUBTITLE_JOINT,
                },
            )
        return data
