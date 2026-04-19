from repositories.Interfaces.i_rengen_apparatus_db import IRengenApparatusDB
from repositories.Interfaces.i_voltage_tube_db import IVoltageTubeDB
from services.Interfaces.i_dataChanger import IDataChanger
from services.Changers.param_choice import is_scalar_choice
from services.Changers.xray_max_kv_by_material_table import (
    filter_rengen_apparatus_rows,
    format_table_kv_text,
    max_permissible_kv_for_card,
)
from services.tech_card import TechCardData


BLOCK_SOURCE = "ИСХОДНЫЕ ДАННЫЕ"
PARAM_APPARATUS = "ИИИ"
LEGACY_PARAM_APPARATUS = "ИИИ Рентгеновский аппарат"
PARAM_FOCAL_SPOT = "Размер фокусного пятна ИИИ, мм"
PARAM_VOLTAGE = "Напряжение на рентгеновской трубке, не более, кВ"
ALT_PARAM_VOLTAGE = "Напряжение на рентгеновской  трубке, не более, кВ"


def _non_empty_text(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _apparatus_display_value(row: dict) -> str | None:
    return _non_empty_text(row.get("val")) or _non_empty_text(row.get("name"))


def _apparatus_catalog(rows: list[dict]) -> list[dict]:
    catalog = []
    for row in rows:
        display_value = _apparatus_display_value(row)
        if display_value is None:
            continue
        catalog.append({"id": row.get("id"), "name": display_value})
    return catalog


def _find_existing_param_name(
    data: TechCardData, block_name: str, param_names
) -> str | None:
    names = (param_names,) if isinstance(param_names, str) else tuple(param_names)
    for param_name in names:
        if data.has_block_and_param(block_name, param_name):
            return param_name
    return None


def _ensure_apparatus_param_name(data: TechCardData) -> str:
    if data.has_block_and_param(BLOCK_SOURCE, PARAM_APPARATUS):
        return PARAM_APPARATUS
    if data.has_block_and_param(BLOCK_SOURCE, LEGACY_PARAM_APPARATUS):
        data.update_param(
            BLOCK_SOURCE,
            LEGACY_PARAM_APPARATUS,
            {"name": PARAM_APPARATUS},
        )
    return PARAM_APPARATUS


class RengenApparatusFromDb(IDataChanger[TechCardData]):
    """
    Блок «ИСХОДНЫЕ ДАННЫЕ»: список ИИИ из rengen_apparatus; предел кВ из public.voltage_tube —
    максимально допустимое напряжение: в списке остаются аппараты, у которых макс. кВ трубки
    не выше этого предела. В «Напряжение …, не более, кВ»
    пишется предел из voltage_tube (при нехватке данных — 0); из аппарата напряжение не копируем.
    """

    def __init__(self, db: IRengenApparatusDB, voltage_tube_db: IVoltageTubeDB):
        self._db = db
        self._vt = voltage_tube_db

    def _apply_table_voltage_limit(self, data: TechCardData) -> None:
        s = format_table_kv_text(max_permissible_kv_for_card(data, self._vt))
        self._set_or_insert_param(
            data,
            PARAM_VOLTAGE,
            s,
            9,
            aliases=(ALT_PARAM_VOLTAGE,),
        )

    def _set_or_insert_param(
        self,
        data: TechCardData,
        param_name: str,
        value,
        insert_id: int,
        aliases=(),
    ) -> None:
        actual_name = _find_existing_param_name(
            data, BLOCK_SOURCE, (param_name,) + tuple(aliases)
        )
        if actual_name is not None:
            data.set_param_value(BLOCK_SOURCE, actual_name, value)
            return
        data.insert_param_to_block(
            BLOCK_SOURCE,
            insert_id,
            {"name": param_name, "val": value},
        )

    def changeData(self, data: TechCardData) -> TechCardData:
        if not data.has_block(BLOCK_SOURCE):
            return data

        rows = self._db.get_rengen_apparatus()
        if not rows:
            return data

        rows = filter_rengen_apparatus_rows(rows, data, self._vt)

        self._apply_table_voltage_limit(data)

        apparatus_names = [
            apparatus_name
            for apparatus_name in (_apparatus_display_value(row) for row in rows)
            if apparatus_name is not None
        ]
        apparatus_catalog = _apparatus_catalog(rows)

        apparatus_param_name = _ensure_apparatus_param_name(data)
        apparatus_value = None
        if data.has_block_and_param(BLOCK_SOURCE, apparatus_param_name):
            apparatus_value = data.get_param_value(BLOCK_SOURCE, apparatus_param_name)

        if data.has_block_and_param(BLOCK_SOURCE, apparatus_param_name):
            data.update_param(
                BLOCK_SOURCE,
                apparatus_param_name,
                {"options": apparatus_catalog},
            )

        if is_scalar_choice(apparatus_value):
            key = str(apparatus_value).strip()
            still_allowed = any(
                key == str(r.get("id"))
                or key == (_apparatus_display_value(r) or "")
                for r in rows
            )
            if still_allowed:
                apparatus_row = self._db.get_rengen_apparatus_by_name_or_id(key)
                if not apparatus_row:
                    return data

                self._set_or_insert_param(
                    data,
                    PARAM_FOCAL_SPOT,
                    apparatus_row.get("focal_spot_size"),
                    8,
                )
                self._apply_table_voltage_limit(data)
                return data

        self._set_or_insert_param(data, PARAM_APPARATUS, apparatus_names, 7)
        data.update_param(
            BLOCK_SOURCE,
            PARAM_APPARATUS,
            {"options": apparatus_catalog},
        )
        return data
