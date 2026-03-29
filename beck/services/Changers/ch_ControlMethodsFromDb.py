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
    Блок «ОТК РК…»: параметр «МЕТОДИКА КОНТРОЛЯ» — загрузка справочника (массив имён).
    Заполняет только если значения нет или оно пустое; непустой массив не трогаем
    (справочник уже выдан). Одиночный выбор пользователя — не этот чейнджер.
    """

    BLOCK_NAME = (
        "ОПЕРАЦИОННАЯ ТЕХНОЛОГИЧЕСКАЯ КАРТА РАДИОГРАФИЧЕСКОГО КОНТРОЛЯ "
        "СВАРНЫХ СОЕДИНЕНИЙ"
    )
    PARAM_NAME = "МЕТОДИКА КОНТРОЛЯ"

    def __init__(self, db: IControlMethodsDB):
        self._db = db

    def changeData(self, data: TechCardData) -> TechCardData:
        if not data.has_block(self.BLOCK_NAME):
            return data
        if data.has_block_and_param(self.BLOCK_NAME, self.PARAM_NAME):
            if not _is_empty_val(data.get_param_value(self.BLOCK_NAME, self.PARAM_NAME)):
                return data

        rows = self._db.get_control_methods()
        names = [r["name"] for r in rows if r.get("name") is not None]

        if data.has_block_and_param(self.BLOCK_NAME, self.PARAM_NAME):
            data.set_param_value(self.BLOCK_NAME, self.PARAM_NAME, names)
        else:
            data.add_param_to_block(
                self.BLOCK_NAME, {"name": self.PARAM_NAME, "val": names}
            )
        return data
