import json
from typing import Any, Dict, List
from pathlib import Path

from repositories.PostgreDbShablov import PostgreDbShablov
from services.tech_card import TechCardData


class PostgreDbShablovGazprom(PostgreDbShablov):
    GAZPROM_METHODOLOGY = 1
    DISPLAY_MODE_NUMBER_ONLY = "number_only"
    DISPLAY_MODE_IMAGE_FULL = "image_full"
    RES_DIR = Path(__file__).resolve().parent.parent / "res"

    BLOCK_LAYOUT: Dict[int, Dict[str, Any]] = {
        1: {
            "name": "Объект контроля - производственное контрольное сварное соединение",
            "fields": [
                {"id": "1", "name": "Предприятие-изготовитель", "options_key": "manufacturers"},
                {"id": "2", "name": "Контролируемое оборудование", "default": "Контрольное сварное соединение"},
                {"id": "3", "name": "№ чертежа", "options_key": "drawing_numbers"},
                {"id": "4", "name": "Контролируемый элемент", "options_key": "controlled_elements"},
                {"id": "5", "name": "Чертеж детали", "options_key": "detail_drawings"},
                {"id": "6", "name": "Тип сварного соединения", "options_key": "welded_joint_types"},
                {"id": "7", "name": "Обозначение", "options_key": "designations"},
                {"id": "8", "name": "Способ сварки", "options_key": "welding_methods"},
                {"id": "9", "name": "Основной металл", "options_key": "metals"},
                {"id": "10", "name": "Сварочный материал", "options_key": "welding_materials"},
            ],
        },
        2: {
            "name": "Документация, по которой производится контроль",
            "fields": [
                {"id": "1", "name": "Нормативная", "options_key": "documentation_normative"},
                {"id": "2", "name": "Методическая", "options_key": "documentation_methodical"},
            ],
        },
        3: {
            "name": "Требования к технологическому контролю и оценке качества",
            "fields": [
                {"id": "1", "name": "Категория сварного соединения", "options_key": "welded_joint_categories"},
                {"id": "2", "name": "Объем контроля, %", "options_key": "scope_of_controls"},
            ],
        },
        4: {
            "name": "Тип и размеры контролируемого элемента",
            "fields": [
                {"id": "1", "name": "Тип контролируемого элемента", "options_key": "welded_joint_types"},
                {"id": "2", "name": "Размеры, мм:", "default": "См. подпункты"},
                {"id": "2.1", "name": "Наружный диаметр штуцера D", "typeData": "double"},
                {"id": "2.2", "name": "Толщина стенки штуцера S", "typeData": "double"},
                {"id": "2.3", "name": "Толщина стенки основного металла H", "typeData": "double"},
                {"id": "2.4", "name": "Катет шва по основному металлу e", "typeData": "double"},
                {"id": "2.5", "name": "Катет шва по патрубку e'", "typeData": "double"},
                {"id": "2.6", "name": "Ширина околошовной зоны l", "typeData": "double"},
                {"id": "2.7", "name": "Толщина расплавляемой вставки b", "typeData": "double"},
            ],
        },
        5: {
            "name": "Средства контроля",
            "fields": [
                {"id": "1", "name": "Источник излучения", "options_key": "radiation_sources"},
                {"id": "2", "name": "Диаметр фокусного пятна, мм", "options_key": "focal_spot_diameters", "typeData": "double"},
                {"id": "3", "name": "Тип радиографической пленки", "options_key": "radiographic_film_types"},
                {"id": "4", "name": "Зарядка пленки в кассету", "options_key": "film_loading_types"},
                {"id": "5", "name": "Тип и номер эталона чувствительности", "options_key": "sensitivity_standard_types"},
                {"id": "6", "name": "Набор маркировочных знаков", "options_key": "marking_sign_types"},
                {"id": "7", "name": "Кассета нестандартная", "options_key": "non_standard_cassettes"},
                {"id": "8", "name": "Денситометр", "options_key": "densitometer_types"},
                {"id": "9", "name": "Негатоскоп", "options_key": "negatoscope_types"},
                {"id": "10", "name": "Линейка измерительная", "options_key": "ruler_types"},
                {"id": "11", "name": "Угломер (транспортир)", "options_key": "protractor_types"},
                {"id": "12", "name": "Лупа измерительная", "options_key": "magnifier_types"},
                {"id": "13", "name": "Краскометр (дефектометр)", "options_key": "paint_detector_types"},
                {"id": "14", "name": "Набор фотохимикатов для ручной обработки"},
                {"id": "15", "name": "Проявочная машина-автомат", "options_key": "photo_processing_automatic"},
            ],
        },
        6: {
            "name": "Параметры и схема контроля",
            "fields": [
                {"id": "1", "name": "Схема просвечивания", "options_key": "transmission_schemes"},
                {"id": "2", "name": "Угол просвечивания от нормали к пленке α, °", "typeData": "double"},
                {"id": "3", "name": "Радиационная толщина (S + e/2/cos(α)), мм", "typeData": "double"},
                {"id": "4", "name": "Требуемая чувствительность контролю, мм", "typeData": "double"},
                {"id": "5", "name": "Напряжение на аноде рентгеновской трубки, кВ", "typeData": "double"},
                {"id": "6", "name": "Расстояние от источника излучения до поверхности контролируемого сварного соединения f, мм, не менее", "typeData": "double"},
                {"id": "7", "name": "Число экспозиций, шт", "typeData": "int"},
                {"id": "8", "name": "Число контролируемых участков, шт", "typeData": "int"},
                {"id": "9", "name": "Размер участка (длина×ширина), мм"},
                {"id": "10", "name": "Достаточные размеры пленки с учетом размеров зоны оценки, эталона и маркировочных знаков"},
            ],
        },
        7: {
            "name": "Подготовка контролируемого элемента",
            "fields": [
                {"id": "1", "name": "Требования к качеству поверхности", "options_key": "surface_quality_requirements"},
                {"id": "2", "name": "Разметка на участки", "options_key": "marking_sections"},
            ],
        },
        8: {
            "name": "Условия и порядок проведения контроля",
            "fields": [
                {"id": "1", "name": "Место проведения контроля", "options_key": "control_places"},
                {"id": "2", "name": "Состав рабочего звена", "options_key": "working_link_compositions"},
                {"id": "3", "name": "Диапазон рабочей температуры, °С", "options_key": "temperature_ranges"},
                {"id": "4", "name": "Последовательность технологических операций", "default": "См. подпункты"},
                {"id": "4.1", "name": "Отметить маркером на сварном соединении место установки кассеты. Установить на основном металле - контролируемом элементе - свинцовые ограничительные метки и маркировочные знаки. Маркировка должна иметь следующую информацию: шифр дефектоскописта; шифр объекта (заводской номер изделия, номер заключения); номер стыка и просвечиваемого участка; клеймо сварщика"},
                {"id": "4.2", "name": "Отрегулировать взаимное расположение источника излучения и контролируемого элемента согласно схеме просвечивания. Выполнить экспонирование радиографической пленки"},
                {"id": "4.3", "name": "По окончании просвечивания снять экспонированную пленку с наплавки"},
                {"id": "4.4", "name": "Контроль участка проводится за одну экспозицию. Для просвечивания следующего участка повторить операции 8.4.1 - 8.4.3"},
                {"id": "4.5", "name": "Выполнить фотообработку экспонированной рентгеновской пленки в соответствии с рекомендациями завода-изготовителя (Фотообработка в кюветах разрешена)"},
                {"id": "4.5.1", "name": "Фотообработка автоматическая", "options_key": "photo_processing_automatic"},
                {"id": "4.5.2", "name": "Время проявления при танковой фотообработке, мин", "options_key": "development_times"},
            ],
        },
        9: {
            "name": "Расшифровка радиографических снимков",
            "fields": [
                {"id": "1", "name": "Просмотр и расшифровку снимков выполняют после их полного высыхания в затемненном помещении с применением негатоскопа"},
                {"id": "2", "name": "Снимки допускаются к расшифровке, если они удовлетворяют следующим требованиям"},
                {"id": "3", "name": "Измерение размеров выявленных несплошностей"},
                {"id": "4", "name": "Измерение при расшифровке снимков размеры следует округлять до ближайших значений из ряда 0,2; 0,3; 0,4; 0,5; 0,6; 0,8; 1,0; 1,2; 1,5; 2,0; 2,5; 3,0; 3,5 и 4,0 мм или ближайших целых значений в мм для измеренных размеров более 4,0 мм"},
            ],
        },
        10: {
            "name": "Оценка качества",
            "fields": [
                {"id": "1", "name": "Качество наплавки считается удовлетворительным, если на снимках не будут зафиксированы трещины и непровары, недопустимые включения"},
                {"id": "2", "name": "Нормы допустимости одиночных включений и скоплений для расчетной высоты сварного шва"},
                {"id": "3", "name": "Выявленные включения, наибольший размер которых менее значения 0,3 мм, при оценке качества сварных соединений не учитываются"},
                {"id": "4", "name": "Любую совокупность включений (одиночных включений, групп включений), которая может быть вписана в прямоугольник, рассматривают как одно включение"},
                {"id": "5", "name": "При отсутствии одиночных крупных включений, в том числе принимаемых за указанные включения по п. 10.4, или при их количестве, менее допускаемого по нормам табл. 10.2, а также при их допустимом в совокупности количестве одиночные включения и/или одиночные скопления допускаемых размеров без их учета при подсчете суммарной площади одиночных включений и одиночных скоплений"},
                {"id": "6", "name": "Результаты оценки допустимости по п. 10.1 - 10.5 и выводы о качестве контролируемого элемента занести в рабочий журнал"},
                {"id": "7", "name": "Результаты расшифровки и оценки качества записать в протокол/заключение по принятой форме"},
            ],
        },
    }

    OPTIONS_QUERIES: Dict[str, Dict[str, Any]] = {
        "manufacturers": {"query": "SELECT DISTINCT name FROM manufacturers WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "drawing_numbers": {"query": "SELECT DISTINCT name FROM drawing_numbers WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "controlled_elements": {"query": "SELECT DISTINCT name FROM controlled_elements WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "detail_drawings": {"query": "SELECT DISTINCT name FROM detail_drawings WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "welded_joint_types": {"query": "SELECT DISTINCT name FROM welded_joint_types WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "designations": {"query": "SELECT DISTINCT name FROM designations WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "welding_methods": {"query": "SELECT DISTINCT name FROM welding_methods WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "metals": {"query": "SELECT DISTINCT name FROM metals WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "welding_materials": {"query": "SELECT DISTINCT name FROM welding_materials WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "documentation_normative": {"query": "SELECT DISTINCT name FROM documentation WHERE LOWER(type) LIKE '%норм%' ORDER BY name"},
        "documentation_methodical": {"query": "SELECT DISTINCT name FROM documentation WHERE LOWER(type) LIKE '%метод%' ORDER BY name"},
        "welded_joint_categories": {"query": "SELECT DISTINCT name FROM welded_joint_categories WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "scope_of_controls": {"query": "SELECT DISTINCT name FROM scope_of_controls WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "radiation_sources": {"query": "SELECT DISTINCT name FROM radiation_sources WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "focal_spot_diameters": {"query": "SELECT DISTINCT focal_spot_diameter FROM radiation_sources WHERE focal_spot_diameter IS NOT NULL ORDER BY focal_spot_diameter", "key": "focal_spot_diameter"},
        "radiographic_film_types": {"query": "SELECT DISTINCT name FROM radiographic_film_types WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "film_loading_types": {"query": "SELECT DISTINCT name FROM film_loading_types WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "sensitivity_standard_types": {"query": "SELECT DISTINCT name FROM sensitivity_standard_types WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "marking_sign_types": {"query": "SELECT DISTINCT name FROM marking_sign_types WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "non_standard_cassettes": {"query": "SELECT DISTINCT name FROM non_standard_cassettes WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "densitometer_types": {"query": "SELECT DISTINCT name FROM densitometer_types WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "negatoscope_types": {"query": "SELECT DISTINCT name FROM negatoscope_types WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "ruler_types": {"query": "SELECT DISTINCT name FROM ruler_types WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "protractor_types": {"query": "SELECT DISTINCT name FROM protractor_types WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "magnifier_types": {"query": "SELECT DISTINCT name FROM magnifier_types WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "paint_detector_types": {"query": "SELECT DISTINCT name FROM paint_detector_types WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "photo_processing_automatic": {"query": "SELECT DISTINCT name FROM photo_processing_automatic WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "transmission_schemes": {"query": "SELECT DISTINCT reference FROM transmission_schemes WHERE reference IS NOT NULL AND reference <> '' ORDER BY reference", "key": "reference"},
        "surface_quality_requirements": {"query": "SELECT DISTINCT name FROM surface_quality_requirements WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "marking_sections": {"query": "SELECT DISTINCT name FROM marking_sections WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "control_places": {"query": "SELECT DISTINCT name FROM control_places WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "working_link_compositions": {"query": "SELECT DISTINCT name FROM working_link_compositions WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "temperature_ranges": {"query": "SELECT DISTINCT name FROM temperature_ranges WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
        "development_times": {"query": "SELECT DISTINCT name FROM development_times WHERE name IS NOT NULL AND name <> '' ORDER BY name"},
    }

    OPERATION_FIELD_IDS = ["4.1", "4.2", "4.3", "4.4", "4.5"]
    SCHEME_BLOCK_ID = 6
    SCHEME_PARAM_ID = "1"

    def _is_db_available(self) -> bool:
        return bool(self.conn and self.cursor)

    def _create_card(self) -> TechCardData:
        return TechCardData(
            typeObjectControl="Контролируемый элемент",
            methodology=self.GAZPROM_METHODOLOGY,
            params={},
        )

    def _normalise_value(self, value: Any) -> Any:
        if value is None:
            return ""
        if isinstance(value, (dict, list)):
            return value
        return str(value)

    def _get_default_display_mode(self, block_id: int, param_id: str) -> str | None:
        if block_id in (9, 10):
            return self.DISPLAY_MODE_NUMBER_ONLY
        if block_id == 8 and str(param_id) in {"4", "4.1", "4.2", "4.3", "4.4", "4.5"}:
            return self.DISPLAY_MODE_NUMBER_ONLY
        return None

    def _fetch_distinct_values(self, query: str, params: tuple = (), key: str = "name") -> List[str]:
        rows = self._fetch_all_rows(query, params)
        result: List[str] = []
        for row in rows:
            value = row.get(key)
            if value in (None, ""):
                continue
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            result.append(str(value))
        return result

    def _join_rows(self, rows: List[Dict[str, Any]], key: str = "name") -> str:
        values = []
        for row in rows:
            value = row.get(key)
            if value in (None, ""):
                continue
            values.append(str(value))
        return "; ".join(values)

    def _summarise_json(self, value: Any) -> str:
        if value in (None, "", [], {}):
            return ""
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)

    def _get_param(self, source: TechCardData | Dict[int, Dict[str, Any]], block_id: int, param_id: str) -> Dict[str, Any] | None:
        blocks = source.params if isinstance(source, TechCardData) else source
        block = blocks.get(block_id) or blocks.get(str(block_id))
        if not isinstance(block, dict):
            return None
        params = block.get("params", {})
        if not isinstance(params, dict):
            return None
        return params.get(str(param_id))

    def _get_param_value(self, source: TechCardData | Dict[int, Dict[str, Any]], block_id: int, param_id: str) -> str:
        param = self._get_param(source, block_id, param_id)
        if not isinstance(param, dict):
            return ""
        return str(param.get("val") or "").strip()

    def _get_param_selected_id(self, source: TechCardData | Dict[int, Dict[str, Any]], block_id: int, param_id: str) -> int | None:
        param = self._get_param(source, block_id, param_id)
        if not isinstance(param, dict):
            return None

        selected_id = param.get("selectedId")
        if selected_id in (None, ""):
            value = param.get("val")
            if isinstance(value, dict):
                selected_id = value.get("id")

        try:
            return int(selected_id) if selected_id not in (None, "") else None
        except (TypeError, ValueError):
            return None

    def _resolve_welded_joint_type_id(self, source: TechCardData | Dict[int, Dict[str, Any]]) -> int | None:
        joint_type_name = (
            self._get_param_value(source, 4, "1")
            or self._get_param_value(source, 1, "6")
        )
        if not joint_type_name:
            return None

        row = self._fetch_one_row(
            """
            SELECT id
            FROM welded_joint_types
            WHERE name = %s
            LIMIT 1
            """,
            (joint_type_name,),
        )
        if not row:
            return None
        try:
            return int(row.get("id"))
        except (TypeError, ValueError):
            return None

    def _resolve_drawing_number_id(self, source: TechCardData | Dict[int, Dict[str, Any]]) -> int | None:
        drawing_number_name = self._get_param_value(source, 1, "3")
        if not drawing_number_name:
            return None

        row = self._fetch_one_row(
            """
            SELECT id
            FROM drawing_numbers
            WHERE name = %s
            LIMIT 1
            """,
            (drawing_number_name,),
        )
        if not row:
            return None
        try:
            return int(row.get("id"))
        except (TypeError, ValueError):
            return None

    def _resolve_designation_id(self, source: TechCardData | Dict[int, Dict[str, Any]]) -> int | None:
        designation_name = self._get_param_value(source, 1, "7")
        drawing_number_id = self._resolve_drawing_number_id(source)
        if not designation_name:
            return None

        if drawing_number_id is not None:
            row = self._fetch_one_row(
                """
                SELECT id
                FROM designations
                WHERE name = %s AND drawing_number_id = %s
                LIMIT 1
                """,
                (designation_name, drawing_number_id),
            )
        else:
            row = self._fetch_one_row(
                """
                SELECT id
                FROM designations
                WHERE name = %s
                LIMIT 1
                """,
                (designation_name,),
            )

        if not row:
            return None
        try:
            return int(row.get("id"))
        except (TypeError, ValueError):
            return None

    def _resolve_controlled_element_id(self, source: TechCardData | Dict[int, Dict[str, Any]]) -> int | None:
        element_name = self._get_param_value(source, 1, "4")
        if not element_name:
            return None

        row = self._fetch_one_row(
            """
            SELECT id
            FROM controlled_elements
            WHERE name = %s
            LIMIT 1
            """,
            (element_name,),
        )
        if not row:
            return None
        try:
            return int(row.get("id"))
        except (TypeError, ValueError):
            return None

    def _get_transmission_scheme_foreign_keys(self) -> List[Dict[str, Any]]:
        return self._fetch_all_rows(
            """
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
              ON ccu.constraint_name = tc.constraint_name
             AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public'
              AND tc.table_name = 'transmission_schemes'
            ORDER BY kcu.ordinal_position
            """
        )

    def _build_transmission_scheme_context(self, source: TechCardData | Dict[int, Dict[str, Any]]) -> Dict[str, int | None]:
        return {
            "welded_joint_types": self._resolve_welded_joint_type_id(source),
            "drawing_numbers": self._resolve_drawing_number_id(source),
            "designations": self._resolve_designation_id(source),
            "controlled_elements": self._resolve_controlled_element_id(source),
        }

    def _get_transmission_scheme_rows(self, source: TechCardData | Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
        foreign_keys = self._get_transmission_scheme_foreign_keys()
        if not foreign_keys:
            return self._fetch_all_rows(
                """
                SELECT id, reference
                FROM transmission_schemes
                ORDER BY id
                """
            )

        context = self._build_transmission_scheme_context(source)
        conditions = []
        params: List[Any] = []

        for foreign_key in foreign_keys:
            column_name = str(foreign_key.get("column_name") or "")
            foreign_table_name = str(foreign_key.get("foreign_table_name") or "")
            if not column_name:
                continue

            selected_parent_id = context.get(foreign_table_name)
            if selected_parent_id is None:
                conditions.append(f"ts.{column_name} IS NULL")
            else:
                conditions.append(f"(ts.{column_name} IS NULL OR ts.{column_name} = %s)")
                params.append(selected_parent_id)

        query = """
            SELECT ts.id, ts.reference
            FROM transmission_schemes ts
        """
        if conditions:
            query += "\nWHERE " + "\n  AND ".join(conditions)
        query += "\nORDER BY ts.id"

        return self._fetch_all_rows(query, tuple(params))

    def _get_quality_assessment_rows(self, designation_id: Any, drawing_number_id: Any) -> List[Dict[str, Any]]:
        if not designation_id:
            return []

        if drawing_number_id:
            return self._fetch_all_rows(
                """
                SELECT parameters
                FROM quality_assessment_types
                WHERE designation_id = %s
                  AND (drawing_numbers_id = %s OR drawing_numbers_id IS NULL)
                ORDER BY
                    CASE WHEN drawing_numbers_id = %s THEN 0 ELSE 1 END,
                    id
                """,
                (designation_id, drawing_number_id, drawing_number_id),
            )

        return self._fetch_all_rows(
            """
            SELECT parameters
            FROM quality_assessment_types
            WHERE designation_id = %s
            ORDER BY id
            """,
            (designation_id,),
        )

    def _get_existing_column_name(self, table_name: str, column_candidates: List[str]) -> str | None:
        if not column_candidates:
            return None

        rows = self._fetch_all_rows(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
            """,
            (table_name,),
        )
        existing_columns = {str(row.get("column_name") or "") for row in rows}

        for column_name in column_candidates:
            if column_name in existing_columns:
                return column_name

        return None

    def _normalise_res_path(self, image_path: Any) -> str | None:
        if image_path in (None, ""):
            return None

        normalised = str(image_path).strip().replace("\\", "/")
        if not normalised:
            return None

        res_marker = "/res/"
        if res_marker in normalised:
            normalised = normalised[normalised.index(res_marker) + 1:]

        if normalised.startswith("res/"):
            return normalised

        if "/" not in normalised:
            candidate_path = self.RES_DIR / normalised
            if candidate_path.exists():
                return f"res/{candidate_path.name}"

        return None

    def _find_scheme_image_fallback(self, transmission_scheme_id: int | None) -> str | None:
        if transmission_scheme_id is None or not self.RES_DIR.exists():
            return None

        for file_path in sorted(self.RES_DIR.glob("*")):
            if not file_path.is_file():
                continue

            stem = file_path.stem.lower()
            if stem in {f"sheme{transmission_scheme_id}", f"scheme{transmission_scheme_id}"}:
                return f"res/{file_path.name}"

        return None

    def _get_transmission_scheme_image_path(self, selected_row: Dict[str, Any] | None) -> str | None:
        if not selected_row:
            return None

        transmission_scheme_id = selected_row.get("id")
        try:
            transmission_scheme_id = int(transmission_scheme_id) if transmission_scheme_id is not None else None
        except (TypeError, ValueError):
            transmission_scheme_id = None

        image_column = self._get_existing_column_name(
            "transmission_schemes",
            ["image", "image_path", "img", "picture", "schema_image", "scheme_image", "path"],
        )
        if image_column and transmission_scheme_id is not None:
            row = self._fetch_one_row(
                f"""
                SELECT {image_column} AS image_path
                FROM transmission_schemes
                WHERE id = %s
                LIMIT 1
                """,
                (transmission_scheme_id,),
            )
            image_path = self._normalise_res_path(row.get("image_path") if row else None)
            if image_path:
                return image_path

        reference_path = self._normalise_res_path(selected_row.get("reference"))
        if reference_path:
            return reference_path

        return self._find_scheme_image_fallback(transmission_scheme_id)

    def _apply_scheme_params(self, blocks: Dict[int, Dict[str, Any]], transmission_scheme_id: int) -> None:
        scheme_params = self._fetch_all_rows(
            """
            SELECT name, val
            FROM params_transmission_scheme
            WHERE transmission_schemes_id = %s
            ORDER BY id
            """,
            (transmission_scheme_id,),
        )

        scheme_field_types = {
            str(field["name"]): field.get("typeData", "string")
            for field in self.BLOCK_LAYOUT[self.SCHEME_BLOCK_ID]["fields"]
            if str(field["id"]) != self.SCHEME_PARAM_ID
        }

        next_param_index = 2
        for row in scheme_params:
            param_name = str(row.get("name") or "").strip()
            if not param_name:
                continue

            self._set_param(
                blocks,
                self.SCHEME_BLOCK_ID,
                str(next_param_index),
                param_name,
                row.get("val"),
                type_data=scheme_field_types.get(param_name, "string"),
            )
            next_param_index += 1

    def _apply_scheme_to_blocks(
        self,
        blocks: Dict[int, Dict[str, Any]],
        source: TechCardData | Dict[int, Dict[str, Any]],
        selected_reference: str | None = None,
        selected_scheme_id: int | None = None,
    ) -> None:
        block = self._ensure_block(blocks, self.SCHEME_BLOCK_ID)
        block["name"] = self.BLOCK_LAYOUT[self.SCHEME_BLOCK_ID]["name"]
        block["params"] = {}

        scheme_rows = self._get_transmission_scheme_rows(source)
        scheme_options = [
            {
                "id": str(row.get("id")),
                "name": str(row.get("reference")),
            }
            for row in scheme_rows
            if row.get("id") is not None and row.get("reference")
        ]

        selected_row = None
        if selected_scheme_id is not None:
            selected_row = next(
                (
                    row
                    for row in scheme_rows
                    if row.get("id") is not None and int(row.get("id")) == selected_scheme_id
                ),
                None,
            )
        if selected_row is None and selected_reference:
            selected_row = next(
                (row for row in scheme_rows if str(row.get("reference") or "") == selected_reference),
                None,
            )
        if selected_row is None and scheme_rows:
            selected_row = scheme_rows[0]

        selected_value = str(selected_row.get("reference")) if selected_row else ""
        self._set_param(
            blocks,
            self.SCHEME_BLOCK_ID,
            self.SCHEME_PARAM_ID,
            "Схема просвечивания",
            selected_value,
            options=scheme_options,
            selected_id=selected_row.get("id") if selected_row else None,
        )

        if selected_row and selected_row.get("id") is not None:
            image_path = self._get_transmission_scheme_image_path(selected_row)
            if image_path:
                self._set_param(
                    blocks,
                    self.SCHEME_BLOCK_ID,
                    "1.1",
                    "Схема просвечивания",
                    image=image_path,
                    display_mode=self.DISPLAY_MODE_IMAGE_FULL,
                )
            self._apply_scheme_params(blocks, int(selected_row["id"]))

    def _ensure_block(self, blocks: Dict[int, Dict[str, Any]], block_id: int) -> Dict[str, Any]:
        block = blocks.get(block_id)
        if block is None:
            block = {
                "name": self.BLOCK_LAYOUT[block_id]["name"],
                "params": {},
            }
            blocks[block_id] = block
        return block

    def _set_param(
        self,
        blocks: Dict[int, Dict[str, Any]],
        block_id: int,
        param_id: str,
        name: str,
        value: Any = "",
        options: List[Any] | None = None,
        type_data: str | None = None,
        image: Any = None,
        display_mode: str | None = None,
        selected_id: Any = None,
    ) -> None:
        block = self._ensure_block(blocks, block_id)
        existing = block["params"].get(str(param_id), {})
        resolved_display_mode = (
            display_mode
            or existing.get("displayMode")
            or self._get_default_display_mode(block_id, str(param_id))
        )
        resolved_selected_id = existing.get("selectedId") if selected_id is None else selected_id
        block["params"][str(param_id)] = {
            "name": name,
            "val": self._normalise_value(value),
            "options": existing.get("options", []) if options is None else options,
            "typeData": existing.get("typeData", "string") if type_data is None else type_data,
        }
        if resolved_display_mode:
            block["params"][str(param_id)]["displayMode"] = resolved_display_mode
        if resolved_selected_id not in (None, ""):
            block["params"][str(param_id)]["selectedId"] = str(resolved_selected_id)
        if image is not None:
            block["params"][str(param_id)]["image"] = image
        elif "image" in existing:
            block["params"][str(param_id)]["image"] = existing["image"]

    def _mark_number_only_params(self, blocks: Dict[int, Dict[str, Any]], block_id: int, param_ids: List[str]) -> None:
        block = self._ensure_block(blocks, block_id)
        params = block.get("params", {})
        if not isinstance(params, dict):
            return

        for param_id in param_ids:
            param = params.get(str(param_id))
            if not isinstance(param, dict):
                continue
            param["displayMode"] = self.DISPLAY_MODE_NUMBER_ONLY

    def _clear_display_mode_params(self, blocks: Dict[int, Dict[str, Any]], block_id: int, param_ids: List[str]) -> None:
        block = self._ensure_block(blocks, block_id)
        params = block.get("params", {})
        if not isinstance(params, dict):
            return

        for param_id in param_ids:
            param = params.get(str(param_id))
            if not isinstance(param, dict):
                continue
            param.pop("displayMode", None)

    def _apply_special_display_modes(self, blocks: Dict[int, Dict[str, Any]]) -> None:
        self._clear_display_mode_params(blocks, 8, ["4.5.1", "4.5.2"])
        self._mark_number_only_params(
            blocks,
            8,
            ["4", "4.1", "4.2", "4.3", "4.4", "4.5"],
        )
        self._mark_number_only_params(blocks, 9, ["1", "2", "3", "4"])
        self._mark_number_only_params(blocks, 10, ["1", "2", "3", "4", "5", "6", "7"])

    def _ensure_block_layout_fields(self, blocks: Dict[int, Dict[str, Any]], block_id: int) -> None:
        block = self._ensure_block(blocks, block_id)
        params = block.setdefault("params", {})

        for field in self.BLOCK_LAYOUT[block_id]["fields"]:
            field_id = str(field["id"])
            existing = params.get(field_id)

            if isinstance(existing, dict):
                existing.setdefault("name", field["name"])
                existing.setdefault("val", self._normalise_value(field.get("default", "")))
                existing.setdefault("options", [])
                existing.setdefault("typeData", field.get("typeData", "string"))
                default_display_mode = self._get_default_display_mode(block_id, field_id)
                if default_display_mode:
                    existing.setdefault("displayMode", default_display_mode)
                continue

            params[field_id] = {
                "name": field["name"],
                "val": self._normalise_value(field.get("default", "")),
                "options": [],
                "typeData": field.get("typeData", "string"),
            }
            default_display_mode = self._get_default_display_mode(block_id, field_id)
            if default_display_mode:
                params[field_id]["displayMode"] = default_display_mode

    def _build_options_map(self) -> Dict[str, List[str]]:
        if not self._is_db_available():
            return {}

        options_map: Dict[str, List[str]] = {}
        for key, config in self.OPTIONS_QUERIES.items():
            options_map[key] = self._fetch_distinct_values(
                config["query"],
                config.get("params", ()),
                config.get("key", "name"),
            )
        return options_map

    def _build_template_blocks(self) -> Dict[int, Dict[str, Any]]:
        options_map = self._build_options_map()
        blocks: Dict[int, Dict[str, Any]] = {}

        for block_id, block_config in self.BLOCK_LAYOUT.items():
            self._ensure_block(blocks, block_id)
            for field in block_config["fields"]:
                self._set_param(
                    blocks,
                    block_id,
                    field["id"],
                    field["name"],
                    value=field.get("default", ""),
                    options=options_map.get(field.get("options_key", ""), []),
                    type_data=field.get("typeData", "string"),
                )

        self._apply_special_display_modes(blocks)
        return blocks

    def _resolve_element_id(self, element_id: int | str | None) -> int:
        try:
            normalised_id = int(element_id or 0)
        except (TypeError, ValueError):
            normalised_id = 0

        if normalised_id > 0:
            return normalised_id

        first_row = self._fetch_one_row(
            """
            SELECT id
            FROM controlled_elements
            ORDER BY id
            LIMIT 1
            """
        )
        if not first_row:
            return 0
        try:
            return int(first_row.get("id") or 0)
        except (TypeError, ValueError):
            return 0

    def _find_dimension_value(self, rows: List[Dict[str, Any]], keywords: List[str], used_indexes: set[int]) -> str:
        for index, row in enumerate(rows):
            if index in used_indexes:
                continue
            text = str(row.get("text") or "").lower()
            if all(keyword in text for keyword in keywords):
                used_indexes.add(index)
                return self._normalise_value(row.get("value"))

        for index, row in enumerate(rows):
            if index in used_indexes:
                continue
            value = self._normalise_value(row.get("value"))
            if value:
                used_indexes.add(index)
                return value

        return ""

    def _fill_block_1(
        self,
        blocks: Dict[int, Dict[str, Any]],
        element_row: Dict[str, Any],
        designation_row: Dict[str, Any] | None,
        designation_params: Dict[str, Any] | None,
        detail_drawings: List[Dict[str, Any]],
    ) -> None:
        self._set_param(blocks, 1, "1", "Предприятие-изготовитель", element_row.get("manufacturer_name"))
        self._set_param(blocks, 1, "2", "Контролируемое оборудование", "Контрольное сварное соединение")
        self._set_param(blocks, 1, "3", "№ чертежа", element_row.get("drawing_number_name"))
        self._set_param(blocks, 1, "4", "Контролируемый элемент", element_row.get("controlled_element_name"))
        self._set_param(blocks, 1, "5", "Чертеж детали", self._join_rows(detail_drawings))
        self._set_param(blocks, 1, "6", "Тип сварного соединения", designation_params.get("welded_joint_type_name") if designation_params else "")
        self._set_param(blocks, 1, "7", "Обозначение", designation_row.get("name") if designation_row else "")
        self._set_param(blocks, 1, "8", "Способ сварки", designation_params.get("welding_method_name") if designation_params else "")
        self._set_param(blocks, 1, "9", "Основной металл", designation_params.get("metal_name") if designation_params else "")
        self._set_param(blocks, 1, "10", "Сварочный материал", designation_params.get("welding_material_name") if designation_params else "")

    def _fill_block_2(self, blocks: Dict[int, Dict[str, Any]]) -> None:
        documentation_rows = self._fetch_all_rows(
            """
            SELECT type, name
            FROM documentation
            ORDER BY id
            """
        )

        normative_rows: List[Dict[str, Any]] = []
        methodical_rows: List[Dict[str, Any]] = []
        other_rows: List[Dict[str, Any]] = []

        for row in documentation_rows:
            type_name = str(row.get("type") or "").strip().lower()
            if "норм" in type_name:
                normative_rows.append(row)
            elif "метод" in type_name:
                methodical_rows.append(row)
            else:
                other_rows.append(row)

        if not normative_rows and other_rows:
            normative_rows.append(other_rows.pop(0))
        if not methodical_rows and other_rows:
            methodical_rows.append(other_rows.pop(0))

        self._set_param(blocks, 2, "1", "Нормативная", self._join_rows(normative_rows))
        self._set_param(blocks, 2, "2", "Методическая", self._join_rows(methodical_rows))

    def _fill_block_3(self, blocks: Dict[int, Dict[str, Any]], designation_params: Dict[str, Any] | None) -> None:
        self._set_param(blocks, 3, "1", "Категория сварного соединения", designation_params.get("welded_joint_category_name") if designation_params else "")
        self._set_param(blocks, 3, "2", "Объем контроля, %", designation_params.get("scope_of_control_name") if designation_params else "")

    def _fill_block_4(
        self,
        blocks: Dict[int, Dict[str, Any]],
        designation_params: Dict[str, Any] | None,
        dimensions_rows: List[Dict[str, Any]],
    ) -> None:
        used_indexes: set[int] = set()
        self._set_param(blocks, 4, "1", "Тип контролируемого элемента", designation_params.get("welded_joint_type_name") if designation_params else "")
        self._set_param(blocks, 4, "2", "Размеры, мм:", "См. подпункты")
        self._set_param(blocks, 4, "2.1", "Наружный диаметр штуцера D", self._find_dimension_value(dimensions_rows, ["наруж", "диаметр", "штуц"], used_indexes))
        self._set_param(blocks, 4, "2.2", "Толщина стенки штуцера S", self._find_dimension_value(dimensions_rows, ["толщ", "стенк", "штуц"], used_indexes))
        self._set_param(blocks, 4, "2.3", "Толщина стенки основного металла H", self._find_dimension_value(dimensions_rows, ["основ", "металл"], used_indexes))
        self._set_param(blocks, 4, "2.4", "Катет шва по основному металлу e", self._find_dimension_value(dimensions_rows, ["катет", "основ"], used_indexes))
        self._set_param(blocks, 4, "2.5", "Катет шва по патрубку e'", self._find_dimension_value(dimensions_rows, ["катет", "патруб"], used_indexes))
        self._set_param(blocks, 4, "2.6", "Ширина околошовной зоны l", self._find_dimension_value(dimensions_rows, ["ширин", "околошов"], used_indexes))
        self._set_param(blocks, 4, "2.7", "Толщина расплавляемой вставки b", self._find_dimension_value(dimensions_rows, ["встав"], used_indexes))

    def _fill_block_5(
        self,
        blocks: Dict[int, Dict[str, Any]],
        designation_params: Dict[str, Any] | None,
        film_loading_rows: List[Dict[str, Any]],
        film_usage_rows: List[Dict[str, Any]],
        control_term_row: Dict[str, Any] | None,
    ) -> None:
        self._set_param(blocks, 5, "1", "Источник излучения", designation_params.get("radiation_source_name") if designation_params else "")
        self._set_param(blocks, 5, "2", "Диаметр фокусного пятна, мм", designation_params.get("focal_spot_diameter") if designation_params else "", type_data="double")
        self._set_param(blocks, 5, "3", "Тип радиографической пленки", self._join_rows(film_usage_rows, "radiographic_film_type_name"))
        self._set_param(blocks, 5, "4", "Зарядка пленки в кассету", self._join_rows(film_loading_rows, "film_loading_type_name"))
        self._set_param(blocks, 5, "5", "Тип и номер эталона чувствительности", designation_params.get("sensitivity_standard_type_name") if designation_params else "")
        self._set_param(blocks, 5, "6", "Набор маркировочных знаков", designation_params.get("marking_sign_type_name") if designation_params else "")
        self._set_param(blocks, 5, "7", "Кассета нестандартная", designation_params.get("non_standard_cassette_name") if designation_params else "")
        self._set_param(blocks, 5, "8", "Денситометр", designation_params.get("densitometer_type_name") if designation_params else "")
        self._set_param(blocks, 5, "9", "Негатоскоп", designation_params.get("negatoscope_type_name") if designation_params else "")
        self._set_param(blocks, 5, "10", "Линейка измерительная", designation_params.get("ruler_type_name") if designation_params else "")
        self._set_param(blocks, 5, "11", "Угломер (транспортир)", designation_params.get("protractor_type_name") if designation_params else "")
        self._set_param(blocks, 5, "12", "Лупа измерительная", designation_params.get("magnifier_type_name") if designation_params else "")
        self._set_param(blocks, 5, "13", "Краскометр (дефектометр)", designation_params.get("paint_detector_type_name") if designation_params else "")
        self._set_param(blocks, 5, "14", "Набор фотохимикатов для ручной обработки")
        self._set_param(blocks, 5, "15", "Проявочная машина-автомат", control_term_row.get("photo_processing_automatic_name") if control_term_row else "")

    def _fill_block_6(
        self,
        blocks: Dict[int, Dict[str, Any]],
        source: TechCardData | Dict[int, Dict[str, Any]],
        selected_reference: str | None = None,
        selected_scheme_id: int | None = None,
    ) -> None:
        self._apply_scheme_to_blocks(blocks, source, selected_reference, selected_scheme_id)

    def _fill_block_7(self, blocks: Dict[int, Dict[str, Any]], preparation_row: Dict[str, Any] | None) -> None:
        self._set_param(blocks, 7, "1", "Требования к качеству поверхности", preparation_row.get("surface_quality_requirement_name") if preparation_row else "")
        self._set_param(blocks, 7, "2", "Разметка на участки", preparation_row.get("marking_section_name") if preparation_row else "")

    def _fill_block_8(
        self,
        blocks: Dict[int, Dict[str, Any]],
        control_term_row: Dict[str, Any] | None,
        operations_rows: List[Dict[str, Any]],
    ) -> None:
        self._set_param(blocks, 8, "1", "Место проведения контроля", control_term_row.get("control_place_name") if control_term_row else "")
        self._set_param(blocks, 8, "2", "Состав рабочего звена", control_term_row.get("working_link_composition_name") if control_term_row else "")
        self._set_param(blocks, 8, "3", "Диапазон рабочей температуры, °С", control_term_row.get("temperature_range_name") if control_term_row else "")
        self._set_param(blocks, 8, "4", "Последовательность технологических операций", "См. подпункты")

        for index, field_id in enumerate(self.OPERATION_FIELD_IDS):
            if index >= len(operations_rows):
                break
            field_name = next(
                field["name"]
                for field in self.BLOCK_LAYOUT[8]["fields"]
                if field["id"] == field_id
            )
            self._set_param(blocks, 8, field_id, field_name, operations_rows[index].get("operation_name"))

        self._set_param(blocks, 8, "4.5.1", "Фотообработка автоматическая", control_term_row.get("photo_processing_automatic_name") if control_term_row else "")
        self._set_param(blocks, 8, "4.5.2", "Время проявления при танковой фотообработке, мин", control_term_row.get("development_time_name") if control_term_row else "")

    def _fill_block_9(self, blocks: Dict[int, Dict[str, Any]], decoding_rows: List[Dict[str, Any]]) -> None:
        values = [row.get("parameters") for row in decoding_rows if row.get("parameters") is not None]
        field_ids = ["1", "2", "3", "4"]
        for index, field_id in enumerate(field_ids):
            if index >= len(values):
                break
            field_name = next(
                field["name"]
                for field in self.BLOCK_LAYOUT[9]["fields"]
                if field["id"] == field_id
            )
            self._set_param(blocks, 9, field_id, field_name, values[index])

    def _fill_block_10(
        self,
        blocks: Dict[int, Dict[str, Any]],
        quality_rows: List[Dict[str, Any]],
        permissible_rows: List[Dict[str, Any]],
    ) -> None:
        quality_values = [row.get("parameters") for row in quality_rows if row.get("parameters") is not None]
        permissible_codes = "; ".join(str(row.get("standard_code")) for row in permissible_rows if row.get("standard_code"))
        permissible_params = "; ".join(
            self._summarise_json(row.get("parameters"))
            for row in permissible_rows
            if row.get("parameters") is not None
        )

        self._set_param(blocks, 10, "1", self.BLOCK_LAYOUT[10]["fields"][0]["name"], quality_values[0] if len(quality_values) > 0 else "")
        self._set_param(blocks, 10, "2", self.BLOCK_LAYOUT[10]["fields"][1]["name"], permissible_codes)
        self._set_param(blocks, 10, "3", self.BLOCK_LAYOUT[10]["fields"][2]["name"], quality_values[1] if len(quality_values) > 1 else "")
        self._set_param(blocks, 10, "4", self.BLOCK_LAYOUT[10]["fields"][3]["name"], quality_values[2] if len(quality_values) > 2 else "")
        self._set_param(blocks, 10, "5", self.BLOCK_LAYOUT[10]["fields"][4]["name"], quality_values[3] if len(quality_values) > 3 else "")
        self._set_param(blocks, 10, "6", self.BLOCK_LAYOUT[10]["fields"][5]["name"], permissible_params)
        self._set_param(blocks, 10, "7", self.BLOCK_LAYOUT[10]["fields"][6]["name"], quality_values[4] if len(quality_values) > 4 else "")

    def _build_full_card_blocks(self, element_id: int) -> Dict[int, Dict[str, Any]]:
        blocks = self._build_template_blocks()
        if not self._is_db_available():
            return blocks

        resolved_element_id = self._resolve_element_id(element_id)
        if not resolved_element_id:
            return blocks

        element_row = self._fetch_one_row(
            """
            SELECT
                ce.id,
                ce.name AS controlled_element_name,
                dn.id AS drawing_number_id,
                dn.name AS drawing_number_name,
                m.name AS manufacturer_name
            FROM controlled_elements ce
            LEFT JOIN drawing_numbers dn ON dn.id = ce.drawing_number_id
            LEFT JOIN manufacturers m ON m.id = dn.manufacturer_id
            WHERE ce.id = %s
            """,
            (resolved_element_id,),
        )
        if not element_row:
            return blocks

        drawing_number_id = element_row.get("drawing_number_id")
        designation_row = self._fetch_one_row(
            """
            SELECT d.id, d.name
            FROM designations d
            WHERE d.drawing_number_id = %s
            ORDER BY d.id
            LIMIT 1
            """,
            (drawing_number_id,),
        ) if drawing_number_id else None
        designation_id = designation_row.get("id") if designation_row else None

        designation_params = self._fetch_one_row(
            """
            SELECT
                dp.welded_joint_type_id,
                wjt.name AS welded_joint_type_name,
                wm.name AS welding_method_name,
                mt.name AS metal_name,
                wmat.name AS welding_material_name,
                wjc.name AS welded_joint_category_name,
                soc.name AS scope_of_control_name,
                rs.name AS radiation_source_name,
                rs.focal_spot_diameter,
                sst.name AS sensitivity_standard_type_name,
                mst.name AS marking_sign_type_name,
                nsc.name AS non_standard_cassette_name,
                mgt.name AS magnifier_type_name,
                dtt.name AS densitometer_type_name,
                ngt.name AS negatoscope_type_name,
                rlt.name AS ruler_type_name,
                ptt.name AS protractor_type_name,
                pdt.name AS paint_detector_type_name
            FROM designation_params dp
            LEFT JOIN welded_joint_types wjt ON wjt.id = dp.welded_joint_type_id
            LEFT JOIN welding_methods wm ON wm.id = dp.welding_method_id
            LEFT JOIN metals mt ON mt.id = dp.metal_id
            LEFT JOIN welding_materials wmat ON wmat.id = dp.welding_material_id
            LEFT JOIN welded_joint_categories wjc ON wjc.id = dp.welded_joint_category_id
            LEFT JOIN scope_of_controls soc ON soc.id = dp.scope_of_control_id
            LEFT JOIN radiation_sources rs ON rs.id = dp.radiation_source_id
            LEFT JOIN sensitivity_standard_types sst ON sst.id = dp.sensitivity_standard_type_id
            LEFT JOIN marking_sign_types mst ON mst.id = dp.marking_sign_type_id
            LEFT JOIN non_standard_cassettes nsc ON nsc.id = dp.non_standard_cassette_id
            LEFT JOIN magnifier_types mgt ON mgt.id = dp.magnifier_type_id
            LEFT JOIN densitometer_types dtt ON dtt.id = dp.densitometer_type_id
            LEFT JOIN negatoscope_types ngt ON ngt.id = dp.negatoscope_type_id
            LEFT JOIN ruler_types rlt ON rlt.id = dp.ruler_type_id
            LEFT JOIN protractor_types ptt ON ptt.id = dp.protractor_type_id
            LEFT JOIN paint_detector_types pdt ON pdt.id = dp.paint_detector_type_id
            WHERE dp.designation_id = %s
            ORDER BY dp.id
            LIMIT 1
            """,
            (designation_id,),
        ) if designation_id else None

        detail_drawings = self._fetch_all_rows(
            """
            SELECT name
            FROM detail_drawings
            WHERE drawing_number_id = %s
            ORDER BY id
            """,
            (drawing_number_id,),
        ) if drawing_number_id else []

        dimensions_rows = self._fetch_all_rows(
            """
            SELECT text, value
            FROM dimensions
            WHERE designation_id = %s
            ORDER BY id
            """,
            (designation_id,),
        ) if designation_id else []

        preparation_row = self._fetch_one_row(
            """
            SELECT
                sqr.name AS surface_quality_requirement_name,
                ms.name AS marking_section_name
            FROM element_preparation ep
            LEFT JOIN surface_quality_requirements sqr ON sqr.id = ep.surface_quality_requirement_id
            LEFT JOIN marking_sections ms ON ms.id = ep.marking_section_id
            WHERE ep.designation_id = %s
            ORDER BY ep.id
            LIMIT 1
            """,
            (designation_id,),
        ) if designation_id else None

        control_term_row = self._fetch_one_row(
            """
            SELECT
                cp.name AS control_place_name,
                wlc.name AS working_link_composition_name,
                tr.name AS temperature_range_name,
                ppa.name AS photo_processing_automatic_name,
                dt.name AS development_time_name
            FROM control_terms ct
            LEFT JOIN control_places cp ON cp.id = ct.control_place_id
            LEFT JOIN working_link_compositions wlc ON wlc.id = ct.working_link_composition_id
            LEFT JOIN temperature_ranges tr ON tr.id = ct.temperature_range_id
            LEFT JOIN photo_processing_automatic ppa ON ppa.id = ct.photo_processing_automatic_id
            LEFT JOIN development_times dt ON dt.id = ct.development_time_id
            WHERE ct.designation_id = %s
            ORDER BY ct.id
            LIMIT 1
            """,
            (designation_id,),
        ) if designation_id else None

        film_loading_rows = self._fetch_all_rows(
            """
            SELECT flt.name AS film_loading_type_name
            FROM film_loading_usage flu
            LEFT JOIN film_loading_types flt ON flt.id = flu.film_loading_type_id
            WHERE flu.designation_id = %s
            ORDER BY flu.id
            """,
            (designation_id,),
        ) if designation_id else []

        film_usage_rows = self._fetch_all_rows(
            """
            SELECT rft.name AS radiographic_film_type_name
            FROM film_usage fu
            LEFT JOIN radiographic_film_types rft ON rft.id = fu.radiographic_film_type_id
            WHERE fu.designation_id = %s
            ORDER BY fu.id
            """,
            (designation_id,),
        ) if designation_id else []

        operations_rows = self._fetch_all_rows(
            """
            SELECT operation_name
            FROM tech_operation_sequences
            WHERE control_term_id IN (
                SELECT id
                FROM control_terms
                WHERE designation_id = %s
            )
            ORDER BY id
            """,
            (designation_id,),
        ) if designation_id else []

        decoding_rows = self._fetch_all_rows(
            """
            SELECT parameters
            FROM radiographic_decoding_types
            WHERE designation_id = %s
            ORDER BY id
            """,
            (designation_id,),
        ) if designation_id else []

        quality_rows = self._get_quality_assessment_rows(designation_id, drawing_number_id)

        permissible_rows = self._fetch_all_rows(
            """
            SELECT pis.standard_code, pis.parameters
            FROM permissible_inclusion_standards pis
            WHERE pis.detail_drawing_id IN (
                SELECT id
                FROM detail_drawings
                WHERE drawing_number_id = %s
            )
            ORDER BY pis.id
            """,
            (drawing_number_id,),
        ) if drawing_number_id else []

        self._fill_block_1(blocks, element_row, designation_row, designation_params, detail_drawings)
        self._fill_block_2(blocks)
        self._fill_block_3(blocks, designation_params)
        self._fill_block_4(blocks, designation_params, dimensions_rows)
        self._fill_block_5(blocks, designation_params, film_loading_rows, film_usage_rows, control_term_row)
        self._fill_block_6(blocks, blocks)
        self._fill_block_7(blocks, preparation_row)
        self._fill_block_8(blocks, control_term_row, operations_rows)
        self._fill_block_9(blocks, decoding_rows)
        self._fill_block_10(blocks, quality_rows, permissible_rows)
        self._apply_special_display_modes(blocks)

        return blocks

    def get_params_for_type(self, type_id) -> TechCardData:
        tech_card = self._create_card()
        tech_card.params = self._build_template_blocks()
        self._fill_block_6(tech_card.params, tech_card.params)
        return tech_card

    def get_all_controlled_element_types(self) -> TechCardData:
        tech_card = TechCardData(methodology=self.GAZPROM_METHODOLOGY)
        tech_card.type = {1: "Контролируемый элемент"}
        return tech_card

    def get_all_objects_by_type_id(self, type_id) -> TechCardData:
        tech_card = self._create_card()
        options = []
        if self._is_db_available():
            options = self._fetch_distinct_values(
                """
                SELECT DISTINCT name
                FROM controlled_elements
                WHERE name IS NOT NULL AND name <> ''
                ORDER BY name
                """
            )
        tech_card.params = {
            1: {
                "name": self.BLOCK_LAYOUT[1]["name"],
                "params": {
                    "4": {
                        "name": "Контролируемый элемент",
                        "val": "",
                        "options": options,
                        "typeData": "string",
                    }
                },
            }
        }
        return tech_card

    def get_all_possible_values_by_param_and_element(self, element_type_id, param_id) -> TechCardData:
        source = self.get_params_for_element(element_type_id) if element_type_id else self.get_params_for_type(0)
        for block in source.params.values():
            params = block.get("params", {})
            if not isinstance(params, dict):
                continue
            param = params.get(str(param_id))
            if not isinstance(param, dict):
                continue

            tech_card = self._create_card()
            tech_card.params = {
                1: {
                    "name": block.get("name", "Параметр"),
                    "params": {
                        str(param_id): {
                            "name": param.get("name"),
                            "val": param.get("options", []),
                            "options": param.get("options", []),
                            "typeData": param.get("typeData", "string"),
                            "displayMode": param.get("displayMode"),
                        }
                    },
                }
            }
            return tech_card

        return self._create_card()

    def sync_tech_card(self, tech_card: TechCardData) -> TechCardData:
        selected_scheme_id = self._get_param_selected_id(tech_card, self.SCHEME_BLOCK_ID, self.SCHEME_PARAM_ID)
        selected_reference = self._get_param_value(tech_card, self.SCHEME_BLOCK_ID, self.SCHEME_PARAM_ID)
        self._fill_block_6(tech_card.params, tech_card, selected_reference, selected_scheme_id)
        return tech_card

    def get_params_for_element(self, element_id: int) -> TechCardData:
        tech_card = self._create_card()
        tech_card.params = self._build_full_card_blocks(element_id)
        return tech_card
