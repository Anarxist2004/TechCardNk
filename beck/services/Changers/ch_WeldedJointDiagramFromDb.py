from services.Interfaces.i_dataChanger import IDataChanger
from repositories.Interfaces.i_type_of_welded_joint_db import ITypeOfWeldedJointDB
from services.tech_card import TechCardData
from services.Changers.param_choice import is_scalar_choice


def _public_image_url(image_ref: str) -> str:
    """Путь для фронта: абсолютный с ведущим / или файл в /res/."""
    s = (image_ref or "").strip()
    if not s:
        return ""
    if s.startswith("/"):
        return s
    return "/res/" + s.lstrip("/")


class WeldedJointDiagramFromDb(IDataChanger[TechCardData]):
    """
    Блок «Объект контроля»: по одиночному выбору «Тип сварного соединения»
    подставляет параметр «Схема» с val.image из type_of_welded_joint.image_ref.
    """

    BLOCK_OBJECT = "Объект контроля"
    PARAM_JOINT = "Тип сварного соединения"
    PARAM_SCHEME = "Схема"

    def __init__(self, db: ITypeOfWeldedJointDB):
        self._db = db

    def changeData(self, data: TechCardData) -> TechCardData:
        if not data.has_block(self.BLOCK_OBJECT):
            return data
        if not data.has_block_and_param(self.BLOCK_OBJECT, self.PARAM_JOINT):
            return data

        joint_val = data.get_param_value(self.BLOCK_OBJECT, self.PARAM_JOINT)
        if not is_scalar_choice(joint_val):
            return data

        image_ref = self._db.get_welded_joint_image_ref(joint_val)
        if not image_ref:
            return data

        url = _public_image_url(image_ref)
        if not url:
            return data

        scheme_val = {"image": url}

        if data.has_block_and_param(self.BLOCK_OBJECT, self.PARAM_SCHEME):
            data.set_param_value(self.BLOCK_OBJECT, self.PARAM_SCHEME, scheme_val)
        else:
            data.add_param_to_block(
                self.BLOCK_OBJECT,
                {"name": self.PARAM_SCHEME, "val": scheme_val},
            )
        return data
