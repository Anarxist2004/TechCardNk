from services.Interfaces.i_dataChanger import IDataChanger
from services.tech_card import TechCardData


def _is_numeric_value(val) -> bool:
    if val is None:
        return False
    if isinstance(val, bool):
        return False
    if isinstance(val, (int, float)):
        return True
    if isinstance(val, str):
        s = val.strip().replace(",", ".")
        if not s:
            return False
        try:
            float(s)
            return True
        except ValueError:
            return False
    return False


def _parse_thickness_mm(val) -> float:
    if isinstance(val, (int, float)):
        return float(val)
    return float(str(val).strip().replace(",", "."))


def _fmt_mm(n: float) -> str:
    r = round(float(n), 6)
    if abs(r - round(r)) < 1e-9:
        return str(int(round(r)))
    s = f"{r:.6f}".rstrip("0").rstrip(".")
    return s


def _width_requirement_text(s_mm: float) -> str:
    """
    Число в «не менее X мм»:
    S ≤ 5 → 5; 5 < S ≤ 20 → номинальная S; S > 20 → 20.
    """
    base = "Ширина сварного шва и околошовная зона размером "
    if s_mm <= 5:
        x = 5.0
    elif s_mm <= 20:
        x = s_mm
    else:
        x = 20.0
    return f"{base}не менее {_fmt_mm(x)} мм с каждой стороны от края шва"


class ControlledZoneWidthStub(IDataChanger[TechCardData]):
    """
    Без БД: при числовой «Номинальная толщина стенки, S, мм» задаёт текст
    «Ширина контролируемой зоны» по толщине.
    """

    BLOCK_OBJECT = "Объект контроля"
    PARAM_THICKNESS = "Номинальная толщина стенки, S, мм"
    PARAM_WIDTH = "Ширина контролируемой зоны"
    SUBTITLE = "Требования к проведению контроля"

    def changeData(self, data: TechCardData) -> TechCardData:
        if not data.has_block(self.BLOCK_OBJECT):
            return data
        if not data.has_block_and_param(self.BLOCK_OBJECT, self.PARAM_THICKNESS):
            return data

        thick = data.get_param_value(self.BLOCK_OBJECT, self.PARAM_THICKNESS)
        if not _is_numeric_value(thick):
            return data

        s_mm = _parse_thickness_mm(thick)
        text = _width_requirement_text(s_mm)

        if data.has_block_and_param(self.BLOCK_OBJECT, self.PARAM_WIDTH):
            data.set_param_value(self.BLOCK_OBJECT, self.PARAM_WIDTH, text)
            data.update_param(
                self.BLOCK_OBJECT,
                self.PARAM_WIDTH,
                {"subtitle": self.SUBTITLE},
            )
        else:
            data.add_param_to_block(
                self.BLOCK_OBJECT,
                {
                    "name": self.PARAM_WIDTH,
                    "val": text,
                    "subtitle": self.SUBTITLE,
                },
            )
        return data
