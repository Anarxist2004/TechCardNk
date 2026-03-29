from services.Interfaces.i_dataChanger import IDataChanger
from repositories.Interfaces.i_regulatory_documents_db import IRegulatoryDocumentsDB
from services.tech_card import TechCardData


def _is_empty_val(val) -> bool:
    if val is None:
        return True
    if isinstance(val, str) and not val.strip():
        return True
    if isinstance(val, (list, tuple)) and len(val) == 0:
        return True
    return False


class RegulatoryDocumentsFromDb(IDataChanger[TechCardData]):
    """
    Блок «ОТК РК…»: параметр «НОРМАТИВНЫЕ ДОКУМЕНТЫ».
    Заполняется из БД только если в техкарте есть «МЕТОДИКА КОНТРОЛЯ» и её значение
    не массив (одиночный выбор: строка или id метода).
    """

    BLOCK_NAME = (
        "ОПЕРАЦИОННАЯ ТЕХНОЛОГИЧЕСКАЯ КАРТА РАДИОГРАФИЧЕСКОГО КОНТРОЛЯ "
        "СВАРНЫХ СОЕДИНЕНИЙ"
    )
    PARAM_METHODOLOGY = "МЕТОДИКА КОНТРОЛЯ"
    PARAM_REGULATORY = "НОРМАТИВНЫЕ ДОКУМЕНТЫ"

    def __init__(self, db: IRegulatoryDocumentsDB):
        self._db = db

    def _find_param(self, block: dict, name: str):
        for p in block.get("params", {}).values():
            if p.get("name") == name:
                return p
        return None

    def _fetch_rows_for_methodology(self, meth_val):
        if isinstance(meth_val, (list, tuple)):
            return None
        if _is_empty_val(meth_val):
            return None
        if isinstance(meth_val, int):
            return self._db.get_regulatory_documents_by_control_method_id(meth_val)
        if isinstance(meth_val, str):
            return self._db.get_regulatory_documents_for_method_name(meth_val.strip())
        return None

    def changeData(self, data: TechCardData) -> TechCardData:
        block = None
        for b in data.params.values():
            if b.get("name") == self.BLOCK_NAME:
                block = b
                break
        if block is None:
            return data

        meth = self._find_param(block, self.PARAM_METHODOLOGY)
        if meth is None:
            return data

        rows = self._fetch_rows_for_methodology(meth.get("val"))
        if rows is None:
            return data

        names = [r["name"] for r in rows if r.get("name") is not None]

        target = self._find_param(block, self.PARAM_REGULATORY)
        if target is not None and not _is_empty_val(target.get("val")):
            return data

        if target is None:
            data.add_param_to_block(
                self.BLOCK_NAME, {"name": self.PARAM_REGULATORY, "val": names}
            )
        else:
            target["val"] = names
        return data
