from repositories.Interfaces.i_materials_db import IMaterialsDB
from services.Interfaces.i_dataChanger import IDataChanger
from services.Changers.param_choice import is_scalar_choice
from services.tech_card import TechCardData


class MaterialsFromDb(IDataChanger[TechCardData]):
    """
    Блок «ИСХОДНЫЕ ДАННЫЕ»: параметр «Материал».
    Если пользователь уже выбрал конкретное значение, не изменяет его.
    Иначе подставляет справочник материалов из БД.
    """

    BLOCK_NAME = (
        "ОПЕРАЦИОННАЯ ТЕХНОЛОГИЧЕСКАЯ КАРТА РАДИОГРАФИЧЕСКОГО КОНТРОЛЯ "
        "СВАРНЫХ СОЕДИНЕНИЙ"
    )
    LEGACY_BLOCK_NAME = "ИСХОДНЫЕ ДАННЫЕ"
    PARAM_NAME = "Материал"

    def __init__(self, db: IMaterialsDB):
        self._db = db

    def _pop_legacy_value(self, data: TechCardData):
        if not data.has_block_and_param(self.LEGACY_BLOCK_NAME, self.PARAM_NAME):
            return None

        legacy_val = data.get_param_value(self.LEGACY_BLOCK_NAME, self.PARAM_NAME)
        data.remove_param_from_block(self.LEGACY_BLOCK_NAME, self.PARAM_NAME)
        return legacy_val

    def changeData(self, data: TechCardData) -> TechCardData:
        if not data.has_block(self.BLOCK_NAME):
            return data

        legacy_val = self._pop_legacy_value(data)

        if data.has_block_and_param(self.BLOCK_NAME, self.PARAM_NAME):
            current_val = data.get_param_value(self.BLOCK_NAME, self.PARAM_NAME)
            if is_scalar_choice(current_val):
                return data
            if is_scalar_choice(legacy_val):
                data.set_param_value(self.BLOCK_NAME, self.PARAM_NAME, legacy_val)
                return data

        rows = self._db.get_materials()
        materials = [r["material"] for r in rows if r.get("material") is not None]

        if data.has_block_and_param(self.BLOCK_NAME, self.PARAM_NAME):
            data.set_param_value(self.BLOCK_NAME, self.PARAM_NAME, materials)
        else:
            value = legacy_val if is_scalar_choice(legacy_val) else materials
            data.add_param_to_block(
                self.BLOCK_NAME,
                {"name": self.PARAM_NAME, "val": value},
            )
        return data
