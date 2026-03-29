from services.Interfaces.i_dataChanger import IDataChanger
from repositories.Interfaces.i_control_methods_db import IControlMethodsDB
from services.tech_card import TechCardData


def _is_empty_val(val) -> bool:
    if val is None:
        return True
    if isinstance(val, str) and not val.strip():
        return True
    if isinstance(val, (list, tuple)) and len(val) == 0:
        return True
    return False


class ControlMethodsFromDb(IDataChanger[TechCardData]):
    """
    Блок «ОТК РК…»: параметр «НАИМЕНОВАНИЕ ОБЪЕКТА».
    Если параметра нет или значение пустое — подставляет массив имён из control_methods.
    """

    BLOCK_NAME = (
        "ОПЕРАЦИОННАЯ ТЕХНОЛОГИЧЕСКАЯ КАРТА РАДИОГРАФИЧЕСКОГО КОНТРОЛЯ "
        "СВАРНЫХ СОЕДИНЕНИЙ"
    )
    PARAM_NAME = "НАИМЕНОВАНИЕ ОБЪЕКТА"

    def __init__(self, db: IControlMethodsDB):
        self._db = db

    def changeData(self, data: TechCardData) -> TechCardData:
        block = None
        for b in data.params.values():
            if b.get("name") == self.BLOCK_NAME:
                block = b
                break
        if block is None:
            return data

        params = block.setdefault("params", {})
        target = None
        for p in params.values():
            if p.get("name") == self.PARAM_NAME:
                target = p
                break

        if target is not None and not _is_empty_val(target.get("val")):
            return data

        rows = self._db.get_control_methods()
        names = [r["name"] for r in rows if r.get("name") is not None]

        if target is None:
            data.add_param_to_block(self.BLOCK_NAME, {"name": self.PARAM_NAME, "val": names})
        else:
            target["val"] = names
        return data
