from services.Interfaces.i_dataChanger import IDataChanger
from repositories.Interfaces.i_cheme_control_db import IChemeControlDB
from services.tech_card import TechCardData
from services.Changers.param_choice import is_scalar_choice


def _public_image_url(image_ref) -> str:
    if image_ref is None:
        return ""
    s = str(image_ref).strip()
    if not s:
        return ""
    if s.startswith("/"):
        return s
    return "/res/" + s.lstrip("/")


def _schemes_val(rows: list) -> list:
    out = []
    for row in rows:
        name = row.get("name")
        if not name:
            continue
        item = {
            "id": row.get("id"),
            "name": name,
        }
        img = _public_image_url(row.get("image_ref"))
        if img:
            item["image"] = img
        out.append(item)
    return out


def _is_scheme_user_selection(val) -> bool:
    """Один выбранный вариант с фронта, а не список допустимых схем (каталог)."""
    if val is None:
        return False
    if isinstance(val, (list, tuple)):
        return False
    if isinstance(val, dict):
        return val.get("id") is not None or bool(
            str(val.get("name") or "").strip()
        )
    if isinstance(val, str) and not val.strip():
        return False
    return isinstance(val, (str, int))


def _find_param_dict(data: TechCardData, block_name: str, param_name: str):
    for block in data.params.values():
        if block.get("name") != block_name:
            continue
        for p in block.get("params", {}).values():
            if p.get("name") == param_name:
                return p
    return None


def _parse_selected_id(param_dict) -> int | None:
    if not param_dict:
        return None
    sid = param_dict.get("selectedId")
    if sid is None or sid == "":
        return None
    try:
        return int(sid)
    except (TypeError, ValueError):
        return None


def _scheme_allowed_for_rows(selected, rows: list, param_dict=None) -> bool:
    """Выбранная схема входит в список, полученный из БД для текущего типа шва."""
    if not rows:
        return False
    allowed_ids = {r["id"] for r in rows if r.get("id") is not None}
    allowed_names = {
        str(r["name"]).strip().lower()
        for r in rows
        if r.get("name") is not None and str(r["name"]).strip()
    }

    iid = _parse_selected_id(param_dict)
    if iid is not None and iid in allowed_ids:
        return True

    if isinstance(selected, dict):
        sid = selected.get("id")
        if sid is not None and sid in allowed_ids:
            return True
        name = selected.get("name")
        if name and str(name).strip().lower() in allowed_names:
            return True
        return False

    if isinstance(selected, int):
        return selected in allowed_ids

    if isinstance(selected, str):
        s = selected.strip()
        if s.isdigit():
            return int(s) in allowed_ids
        return s.lower() in allowed_names

    return False


def _find_matching_row(current, param_dict, rows: list):
    """Строка cheme_control для текущего выбора (учитывается selectedId на параметре)."""
    iid = _parse_selected_id(param_dict)
    if iid is not None:
        for r in rows:
            if r.get("id") == iid:
                return r

    if isinstance(current, dict):
        sid = current.get("id")
        if sid is not None:
            for r in rows:
                if r.get("id") == sid:
                    return r
        name = str(current.get("name") or "").strip()
        if name:
            nl = name.lower()
            for r in rows:
                rn = r.get("name")
                if rn is not None and str(rn).strip().lower() == nl:
                    return r

    if isinstance(current, int):
        for r in rows:
            if r.get("id") == current:
                return r

    if isinstance(current, str):
        s = current.strip()
        if s.isdigit():
            for r in rows:
                if r.get("id") == int(s):
                    return r
        sl = s.lower()
        for r in rows:
            rn = r.get("name")
            if rn is not None and str(rn).strip().lower() == sl:
                return r

    return None


class ControlSchemesFromJointTypeDb(IDataChanger[TechCardData]):
    """
    Блок «ИСХОДНЫЕ ДАННЫ», параметр «схема просвечивания»:
    схемы из cheme_control по weld_type_to_scheme для одиночного «Тип сварного соединения».
    Если на фронте уже выбрана схема и она допустима для текущего набора из БД — val не трогаем.
    """

    BLOCK_OBJECT = "Объект контроля"
    BLOCK_SOURCE = "ИСХОДНЫЕ ДАННЫЕ"
    PARAM_JOINT = "Тип сварного соединения"
    PARAM_SCHEME = "схема просвечивания"

    def __init__(self, db: IChemeControlDB):
        self._db = db

    def changeData(self, data: TechCardData) -> TechCardData:
        if not data.has_block(self.BLOCK_OBJECT):
            return data
        if not data.has_block(self.BLOCK_SOURCE):
            return data
        if not data.has_block_and_param(self.BLOCK_OBJECT, self.PARAM_JOINT):
            return data

        joint_val = data.get_param_value(self.BLOCK_OBJECT, self.PARAM_JOINT)
        if not is_scalar_choice(joint_val):
            return data

        rows = self._db.get_control_schemes_for_welded_joint(joint_val)
        catalog = _schemes_val(rows)

        if data.has_block_and_param(self.BLOCK_SOURCE, self.PARAM_SCHEME):
            current = data.get_param_value(self.BLOCK_SOURCE, self.PARAM_SCHEME)
            param_dict = _find_param_dict(
                data, self.BLOCK_SOURCE, self.PARAM_SCHEME
            )
            if _is_scheme_user_selection(current) and _scheme_allowed_for_rows(
                current, rows, param_dict
            ):
                matched = _find_matching_row(current, param_dict, rows)
                img = (
                    _public_image_url(matched.get("image_ref"))
                    if matched
                    else ""
                )
                data.update_param(
                    self.BLOCK_SOURCE,
                    self.PARAM_SCHEME,
                    {"options": catalog, "image": img},
                )
                return data

            data.set_param_value(self.BLOCK_SOURCE, self.PARAM_SCHEME, catalog)
            data.update_param(
                self.BLOCK_SOURCE,
                self.PARAM_SCHEME,
                {"options": catalog, "image": ""},
            )
        else:
            data.add_param_to_block(
                self.BLOCK_SOURCE,
                {
                    "name": self.PARAM_SCHEME,
                    "val": catalog,
                    "options": catalog,
                    "image": "",
                },
            )
        return data
