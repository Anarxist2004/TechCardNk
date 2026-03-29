from services.Interfaces.i_dataChanger import IDataChanger
from repositories.Interfaces.i_regulatory_documents_db import IRegulatoryDocumentsDB
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


class RegulatoryDocumentsFromDb(IDataChanger[TechCardData]):
    """
    Блок «ОТК РК…»: параметр «НОРМАТИВНЫЕ ДОКУМЕНТЫ».
    Подставляет данные только если «МЕТОДИКА КОНТРОЛЯ» — одиночный выбор (str/int),
    не пустое и не массив (массив = справочник без выбора).
    """

    BLOCK_NAME = (
        "ОПЕРАЦИОННАЯ ТЕХНОЛОГИЧЕСКАЯ КАРТА РАДИОГРАФИЧЕСКОГО КОНТРОЛЯ "
        "СВАРНЫХ СОЕДИНЕНИЙ"
    )
    PARAM_METHODOLOGY = "МЕТОДИКА КОНТРОЛЯ"
    PARAM_REGULATORY = "НОРМАТИВНЫЕ ДОКУМЕНТЫ"

    def __init__(self, db: IRegulatoryDocumentsDB):
        self._db = db

    def _fetch_rows_for_methodology(self, meth_val):
        if not is_scalar_choice(meth_val):
            return None
        if isinstance(meth_val, int):
            return self._db.get_regulatory_documents_by_control_method_id(meth_val)
        return self._db.get_regulatory_documents_for_method_name(meth_val.strip())

    def changeData(self, data: TechCardData) -> TechCardData:
        if not data.has_block(self.BLOCK_NAME):
            return data
        if not data.has_block_and_param(self.BLOCK_NAME, self.PARAM_METHODOLOGY):
            return data

        if data.has_block_and_param(self.BLOCK_NAME, self.PARAM_REGULATORY):
            if not _is_empty_val(
                data.get_param_value(self.BLOCK_NAME, self.PARAM_REGULATORY)
            ):
                return data

        meth_val = data.get_param_value(self.BLOCK_NAME, self.PARAM_METHODOLOGY)
        if not is_scalar_choice(meth_val):
            return data

        rows = self._fetch_rows_for_methodology(meth_val)
        if rows is None:
            return data
        if not rows:
            return data

        names = [r["name"] for r in rows if r.get("name") is not None]

        if data.has_block_and_param(self.BLOCK_NAME, self.PARAM_REGULATORY):
            data.set_param_value(self.BLOCK_NAME, self.PARAM_REGULATORY, names)
        else:
            data.add_param_to_block(
                self.BLOCK_NAME, {"name": self.PARAM_REGULATORY, "val": names}
            )
        return data
