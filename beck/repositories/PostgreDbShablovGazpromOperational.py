from typing import Any, Dict, List

from repositories.PostgreDbShablovGazprom import PostgreDbShablovGazprom
from services.tech_card import TechCardData


class PostgreDbShablovGazpromOperational(PostgreDbShablovGazprom):
    METHODOLOGY_ID = 2
    TYPE_NAME = "Контролируемый элемент"
    HEADER_BLOCK_ID = 1
    OBJECT_BLOCK_ID = 2
    SOURCE_DATA_BLOCK_ID = 3
    SCHEME_BLOCK_ID = 4
    OPERATIONS_BLOCK_ID = 5
    SIGNATURES_BLOCK_ID = 6
    CONTROLLED_ELEMENT_PARAM_ID = "3"
    SCHEME_PARAM_ID = "1"
    OBJECT_IMAGE_PARAM_ID = "90"
    SCHEME_IMAGE_PARAM_ID = "1.1"

    BLOCK_LAYOUT: Dict[int, Dict[str, Any]] = {
        HEADER_BLOCK_ID: {
            "name": "Шапка",
            "fields": [
                {"id": "1", "name": "Наименование организации"},
                {"id": "2", "name": "Номер чертежа (эскиза)"},
                {"id": CONTROLLED_ELEMENT_PARAM_ID, "name": "Наименование объекта", "options_key": "controlled_elements"},
                {"id": "4", "name": "Методика контроля"},
                {"id": "5", "name": "Нормативные документы"},
                {"id": "6", "name": "Шифр"},
                {"id": "7", "name": "Уровень качества"},
            ],
        },
        OBJECT_BLOCK_ID: {
            "name": "Объект контроля",
            "fields": [
                {"id": "1", "name": "Номинальный диаметр трубы, мм"},
                {"id": "2", "name": "Номинальная толщина стенки, S, мм"},
                {"id": "3", "name": "Тип сварного соединения, тип сварки"},
            ],
        },
        SOURCE_DATA_BLOCK_ID: {
            "name": "Исходные данные",
            "fields": [],
        },
        SCHEME_BLOCK_ID: {
            "name": "Схема просвечивания",
            "fields": [
                {"id": SCHEME_PARAM_ID, "name": "Схема просвечивания", "options_key": "transmission_schemes"},
            ],
        },
        OPERATIONS_BLOCK_ID: {
            "name": "Перечень операций РК",
            "fields": [],
        },
        SIGNATURES_BLOCK_ID: {
            "name": "Подписи",
            "fields": [
                {"id": "1", "name": "Разработал - ФИО"},
                {"id": "2", "name": "Разработал - Подпись"},
                {"id": "3", "name": "Разработал - Должность, организация"},
                {"id": "4", "name": "Разработал - Уровень квалификации, № удостоверения"},
                {"id": "5", "name": "Утвердил - ФИО"},
                {"id": "6", "name": "Утвердил - Подпись"},
                {"id": "7", "name": "Утвердил - Должность, организация"},
                {"id": "8", "name": "Утвердил - Уровень квалификации, № удостоверения"},
            ],
        },
    }

    OPTIONS_QUERIES: Dict[str, Dict[str, Any]] = {
        "controlled_elements": {
            "query": """
                SELECT DISTINCT name
                FROM controlled_elements
                WHERE name IS NOT NULL AND name <> ''
                ORDER BY name
            """
        },
        "transmission_schemes": {
            "query": """
                SELECT DISTINCT reference
                FROM transmission_schemes
                WHERE reference IS NOT NULL AND reference <> ''
                ORDER BY reference
            """,
            "key": "reference",
        },
    }

    CREATE_OPTION_CONFIGS: Dict[str, Dict[str, Any]] = {}

    def _create_card(self) -> TechCardData:
        return TechCardData(
            typeObjectControl=self.TYPE_NAME,
            methodology=self.METHODOLOGY_ID,
            params={},
        )

    def _get_default_display_mode(self, block_id: int, param_id: str) -> str | None:
        _ = (block_id, param_id)
        return None

    def _apply_special_display_modes(self, blocks: Dict[int, Dict[str, Any]]) -> None:
        _ = blocks

    def _mark_sync_on_select(self, blocks: Dict[int, Dict[str, Any]], block_id: int, param_id: str) -> None:
        param = self._get_param(blocks, block_id, param_id)
        if isinstance(param, dict):
            param["syncOnSelect"] = True

    def _get_controlled_element_options(self) -> List[Dict[str, str]]:
        rows = self._fetch_all_rows(
            """
            SELECT id, name
            FROM controlled_elements
            WHERE name IS NOT NULL AND name <> ''
            ORDER BY name, id
            """
        )
        options: List[Dict[str, str]] = []

        for row in rows:
            element_id = row.get("id")
            name = str(row.get("name") or "").strip()
            if element_id in (None, "") or not name:
                continue
            options.append({"id": str(element_id), "name": name})

        return options

    def _get_selected_controlled_element_id(self, source: TechCardData | Dict[int, Dict[str, Any]]) -> int | None:
        selected_id = self._get_param_selected_id(source, self.HEADER_BLOCK_ID, self.CONTROLLED_ELEMENT_PARAM_ID)
        if selected_id is not None:
            return selected_id

        element_name = self._get_param_value(source, self.HEADER_BLOCK_ID, self.CONTROLLED_ELEMENT_PARAM_ID)
        if not element_name:
            return None

        row = self._fetch_one_row(
            """
            SELECT id
            FROM controlled_elements
            WHERE name = %s
            ORDER BY id
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

    def _resolve_controlled_element_id(self, source: TechCardData | Dict[int, Dict[str, Any]]) -> int | None:
        return self._get_selected_controlled_element_id(source)

    def _resolve_drawing_number_id(self, source: TechCardData | Dict[int, Dict[str, Any]]) -> int | None:
        element_id = self._get_selected_controlled_element_id(source)
        if element_id is None:
            return None

        row = self._fetch_one_row(
            """
            SELECT drawing_number_id
            FROM controlled_elements
            WHERE id = %s
            LIMIT 1
            """,
            (element_id,),
        )
        if not row:
            return None

        try:
            return int(row.get("drawing_number_id")) if row.get("drawing_number_id") is not None else None
        except (TypeError, ValueError):
            return None

    def _resolve_designation_id(self, source: TechCardData | Dict[int, Dict[str, Any]]) -> int | None:
        drawing_number_id = self._resolve_drawing_number_id(source)
        if drawing_number_id is None:
            return None

        row = self._fetch_one_row(
            """
            SELECT id
            FROM designations
            WHERE drawing_number_id = %s
            ORDER BY id
            LIMIT 1
            """,
            (drawing_number_id,),
        )
        if not row:
            return None

        try:
            return int(row.get("id"))
        except (TypeError, ValueError):
            return None

    def _resolve_welded_joint_type_id(self, source: TechCardData | Dict[int, Dict[str, Any]]) -> int | None:
        designation_id = self._resolve_designation_id(source)
        if designation_id is None:
            return None

        row = self._fetch_one_row(
            """
            SELECT welded_joint_type_id
            FROM designation_params
            WHERE designation_id = %s
            ORDER BY id
            LIMIT 1
            """,
            (designation_id,),
        )
        if not row:
            return None

        try:
            return int(row.get("welded_joint_type_id")) if row.get("welded_joint_type_id") is not None else None
        except (TypeError, ValueError):
            return None

    def _get_documentation_rows(self) -> List[Dict[str, Any]]:
        return self._fetch_all_rows(
            """
            SELECT type, name
            FROM documentation
            WHERE name IS NOT NULL AND name <> ''
            ORDER BY id
            """
        )

    def _split_documentation_rows(self, rows: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        normative_rows: List[Dict[str, Any]] = []
        methodical_rows: List[Dict[str, Any]] = []

        for row in rows:
            type_name = str(row.get("type") or "").strip().lower()
            if "норм" in type_name:
                normative_rows.append(row)
            elif "метод" in type_name:
                methodical_rows.append(row)

        return normative_rows, methodical_rows

    def _build_cipher(self, dimensions_rows: List[Dict[str, Any]]) -> str:
        diameter = self._find_dimension_value(list(dimensions_rows), ["диаметр", "труб"], set())
        thickness = self._find_dimension_value(list(dimensions_rows), ["толщ", "стенк"], set())

        if diameter and thickness:
            return f"ТК-РК {diameter}x{thickness}"
        if diameter:
            return f"ТК-РК {diameter}"
        return "ТК-РК"

    def _build_quality_level(self, designation_params: Dict[str, Any] | None) -> str:
        if not designation_params:
            return ""

        raw_value = str(designation_params.get("welded_joint_category_name") or "").strip()
        if not raw_value:
            return ""

        parts = [part.strip() for part in raw_value.replace(",", " ").split() if part.strip()]
        if len(parts) == 1:
            return parts[0]
        return raw_value

    def _fetch_element_context(self, element_id: int) -> Dict[str, Any]:
        resolved_element_id = self._resolve_element_id(element_id)
        if not resolved_element_id:
            return {}

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
            return {}

        drawing_number_id = element_row.get("drawing_number_id")
        designation_row = self._fetch_one_row(
            """
            SELECT id, name
            FROM designations
            WHERE drawing_number_id = %s
            ORDER BY id
            LIMIT 1
            """,
            (drawing_number_id,),
        ) if drawing_number_id else None
        designation_id = designation_row.get("id") if designation_row else None

        designation_params = self._fetch_one_row(
            """
            SELECT
                dp.designation_id,
                dp.welded_joint_type_id,
                wjt.name AS welded_joint_type_name,
                wjt."refImg" AS welded_joint_ref_img,
                wm.name AS welding_method_name,
                wjc.name AS welded_joint_category_name,
                rs.name AS radiation_source_name,
                rs.focal_spot_diameter,
                sst.name AS sensitivity_standard_type_name
            FROM designation_params dp
            LEFT JOIN welded_joint_types wjt ON wjt.id = dp.welded_joint_type_id
            LEFT JOIN welding_methods wm ON wm.id = dp.welding_method_id
            LEFT JOIN welded_joint_categories wjc ON wjc.id = dp.welded_joint_category_id
            LEFT JOIN radiation_sources rs ON rs.id = dp.radiation_source_id
            LEFT JOIN sensitivity_standard_types sst ON sst.id = dp.sensitivity_standard_type_id
            WHERE dp.designation_id = %s
            ORDER BY dp.id
            LIMIT 1
            """,
            (designation_id,),
        ) if designation_id else None

        dimensions_rows = self._fetch_all_rows(
            """
            SELECT text, value
            FROM dimensions
            WHERE designation_id = %s
            ORDER BY id
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

        engineers_rows = self._fetch_all_rows(
            """
            SELECT
                id,
                "FIO" AS fio,
                organization,
                "Skill level" AS skill_level
            FROM engineers
            ORDER BY id
            """
        )

        return {
            "element_row": element_row,
            "drawing_number_id": drawing_number_id,
            "designation_row": designation_row,
            "designation_id": designation_id,
            "designation_params": designation_params,
            "dimensions_rows": dimensions_rows,
            "film_usage_rows": film_usage_rows,
            "film_loading_rows": film_loading_rows,
            "documentation_rows": self._get_documentation_rows(),
            "engineers_rows": engineers_rows,
        }

    def _fill_header_block(self, blocks: Dict[int, Dict[str, Any]], context: Dict[str, Any]) -> None:
        element_row = context.get("element_row") or {}
        designation_params = context.get("designation_params") or {}
        documentation_rows = context.get("documentation_rows") or []
        dimensions_rows = context.get("dimensions_rows") or []
        normative_rows, methodical_rows = self._split_documentation_rows(documentation_rows)
        methodology_parts = [
            self._join_rows(methodical_rows),
            self._join_rows(normative_rows),
        ]
        methodology_value = "; ".join([part for part in methodology_parts if part])
        controlled_element_options = self._get_controlled_element_options()

        self._set_param(
            blocks,
            self.HEADER_BLOCK_ID,
            "1",
            "Наименование организации",
            element_row.get("manufacturer_name"),
        )
        self._set_param(
            blocks,
            self.HEADER_BLOCK_ID,
            "2",
            "Номер чертежа (эскиза)",
            element_row.get("drawing_number_name"),
        )
        self._set_param(
            blocks,
            self.HEADER_BLOCK_ID,
            self.CONTROLLED_ELEMENT_PARAM_ID,
            "Наименование объекта",
            element_row.get("controlled_element_name"),
            options=controlled_element_options,
            selected_id=element_row.get("id"),
        )
        self._mark_sync_on_select(blocks, self.HEADER_BLOCK_ID, self.CONTROLLED_ELEMENT_PARAM_ID)
        self._set_param(
            blocks,
            self.HEADER_BLOCK_ID,
            "4",
            "Методика контроля",
            methodology_value,
        )
        self._set_param(
            blocks,
            self.HEADER_BLOCK_ID,
            "5",
            "Нормативные документы",
            self._join_rows(normative_rows),
        )
        self._set_param(
            blocks,
            self.HEADER_BLOCK_ID,
            "6",
            "Шифр",
            self._build_cipher(dimensions_rows),
        )
        self._set_param(
            blocks,
            self.HEADER_BLOCK_ID,
            "7",
            "Уровень качества",
            self._build_quality_level(designation_params),
        )

    def _fill_object_block(self, blocks: Dict[int, Dict[str, Any]], context: Dict[str, Any]) -> None:
        block = self._ensure_block(blocks, self.OBJECT_BLOCK_ID)
        block["name"] = self.BLOCK_LAYOUT[self.OBJECT_BLOCK_ID]["name"]
        block["params"] = {}

        designation_params = context.get("designation_params") or {}
        dimensions_rows = context.get("dimensions_rows") or []
        used_indexes: set[int] = set()

        nominal_diameter = self._find_dimension_value(dimensions_rows, ["диаметр", "труб"], used_indexes)
        wall_thickness = self._find_dimension_value(dimensions_rows, ["толщ", "стенк"], used_indexes)

        joint_description_parts = [
            str(designation_params.get("welded_joint_type_name") or "").strip(),
            str(designation_params.get("welding_method_name") or "").strip(),
        ]
        joint_description = ". ".join([part for part in joint_description_parts if part])

        self._set_param(blocks, self.OBJECT_BLOCK_ID, "1", "Номинальный диаметр трубы, мм", nominal_diameter)
        self._set_param(blocks, self.OBJECT_BLOCK_ID, "2", "Номинальная толщина стенки, S, мм", wall_thickness)
        self._set_param(blocks, self.OBJECT_BLOCK_ID, "3", "Тип сварного соединения, тип сварки", joint_description)

        next_param_index = 4
        for index, row in enumerate(dimensions_rows):
            if index in used_indexes:
                continue

            param_name = str(row.get("text") or "").strip()
            value = row.get("value")
            if not param_name and value in (None, ""):
                continue

            self._set_param(
                blocks,
                self.OBJECT_BLOCK_ID,
                str(next_param_index),
                param_name or f"Параметр {next_param_index}",
                value,
            )
            next_param_index += 1

        image_path = self._normalise_res_path(designation_params.get("welded_joint_ref_img"))
        if image_path:
            self._set_param(
                blocks,
                self.OBJECT_BLOCK_ID,
                self.OBJECT_IMAGE_PARAM_ID,
                "Схема сварного соединения",
                image=image_path,
                display_mode=self.DISPLAY_MODE_IMAGE_FULL,
            )

    def _normalise_named_value(self, value: Any) -> str:
        return str(value or "").strip().lower()

    def _append_named_row(
        self,
        blocks: Dict[int, Dict[str, Any]],
        block_id: int,
        next_index: int,
        used_names: set[str],
        name: str,
        value: Any,
    ) -> int:
        normalised_name = self._normalise_named_value(name)
        normalised_value = self._normalise_value(value)

        if not normalised_name or normalised_name in used_names or normalised_value in (None, ""):
            return next_index

        used_names.add(normalised_name)
        self._set_param(blocks, block_id, str(next_index), name, normalised_value)
        return next_index + 1

    def _fill_source_data_block(
        self,
        blocks: Dict[int, Dict[str, Any]],
        context: Dict[str, Any],
        selected_scheme_row: Dict[str, Any] | None,
    ) -> None:
        block = self._ensure_block(blocks, self.SOURCE_DATA_BLOCK_ID)
        block["name"] = self.BLOCK_LAYOUT[self.SOURCE_DATA_BLOCK_ID]["name"]
        block["params"] = {}

        designation_params = context.get("designation_params") or {}
        film_usage_rows = context.get("film_usage_rows") or []
        film_loading_rows = context.get("film_loading_rows") or []
        used_names: set[str] = set()
        next_param_index = 1

        if selected_scheme_row and selected_scheme_row.get("id") is not None:
            scheme_params_rows = self._fetch_all_rows(
                """
                SELECT name, val
                FROM params_transmission_scheme
                WHERE transmission_schemes_id = %s
                ORDER BY id
                """,
                (selected_scheme_row["id"],),
            )

            for row in scheme_params_rows:
                param_name = str(row.get("name") or "").strip()
                param_value = row.get("val")
                next_param_index = self._append_named_row(
                    blocks,
                    self.SOURCE_DATA_BLOCK_ID,
                    next_param_index,
                    used_names,
                    param_name,
                    param_value,
                )

        supplemental_rows = [
            ("ИИИ", designation_params.get("radiation_source_name")),
            ("Размер фокусного пятна ИИИ, мм", designation_params.get("focal_spot_diameter")),
            ("Тип и номер эталона чувствительности", designation_params.get("sensitivity_standard_type_name")),
            ("Тип радиографической пленки", self._join_rows(film_usage_rows, "radiographic_film_type_name")),
            ("Тип загрузки пленки", self._join_rows(film_loading_rows, "film_loading_type_name")),
        ]

        for name, value in supplemental_rows:
            next_param_index = self._append_named_row(
                blocks,
                self.SOURCE_DATA_BLOCK_ID,
                next_param_index,
                used_names,
                name,
                value,
            )

    def _resolve_selected_scheme_row(
        self,
        blocks: Dict[int, Dict[str, Any]],
        selected_scheme_id: int | None = None,
        selected_reference: str | None = None,
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any] | None]:
        scheme_rows = self._get_transmission_scheme_rows(blocks)
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
                (
                    row
                    for row in scheme_rows
                    if str(row.get("reference") or "").strip() == str(selected_reference).strip()
                ),
                None,
            )

        if selected_row is None and scheme_rows:
            selected_row = scheme_rows[0]

        return scheme_rows, selected_row

    def _fill_scheme_block(
        self,
        blocks: Dict[int, Dict[str, Any]],
        scheme_rows: List[Dict[str, Any]],
        selected_row: Dict[str, Any] | None,
    ) -> None:
        block = self._ensure_block(blocks, self.SCHEME_BLOCK_ID)
        block["name"] = self.BLOCK_LAYOUT[self.SCHEME_BLOCK_ID]["name"]
        block["params"] = {}

        scheme_options = [
            {"id": str(row.get("id")), "name": str(row.get("reference"))}
            for row in scheme_rows
            if row.get("id") is not None and row.get("reference")
        ]
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
        self._mark_sync_on_select(blocks, self.SCHEME_BLOCK_ID, self.SCHEME_PARAM_ID)

        image_path = self._get_transmission_scheme_image_path(selected_row)
        if image_path:
            self._set_param(
                blocks,
                self.SCHEME_BLOCK_ID,
                self.SCHEME_IMAGE_PARAM_ID,
                "Схема просвечивания",
                image=image_path,
                display_mode=self.DISPLAY_MODE_IMAGE_FULL,
            )

    def _collect_operation_lines(self, payload: Any, default_step: str) -> List[str]:
        if payload in (None, "", [], {}):
            return []

        if isinstance(payload, list):
            lines: List[str] = []
            for index, item in enumerate(payload, start=1):
                nested_step = f"{default_step}.{index}" if default_step else str(index)
                lines.extend(self._collect_operation_lines(item, nested_step))
            return lines

        if isinstance(payload, dict):
            lines: List[str] = []
            explicit_step = str(payload.get("step") or "").strip()
            current_step = explicit_step or default_step
            title = str(payload.get("title") or payload.get("name") or "").strip()
            description = str(payload.get("description") or "").strip()
            body = self._build_operation_value(payload)

            main_text = ""
            if title and body and body != title:
                main_text = f"{title}: {body}"
            elif title:
                main_text = title
            elif description:
                main_text = description
            elif body:
                main_text = body

            if main_text:
                lines.append(f"{current_step} {main_text}".strip())

            for nested_key in ("procedure", "substeps", "items"):
                nested_payload = payload.get(nested_key)
                if isinstance(nested_payload, list):
                    for index, item in enumerate(nested_payload, start=1):
                        nested_step = f"{current_step}.{index}" if current_step else str(index)
                        lines.extend(self._collect_operation_lines(item, nested_step))

            return lines

        scalar_value = self._format_operation_scalar(payload)
        if not scalar_value:
            return []

        return [f"{default_step} {scalar_value}".strip()]

    def _render_operation_content(self, payload: Any, operation_index: str, content_index: int) -> List[str]:
        parsed_payload = self._parse_json_payload(payload)
        default_step = f"{operation_index}.{content_index}" if operation_index else str(content_index)
        lines = self._collect_operation_lines(parsed_payload, default_step)

        if lines:
            return lines

        scalar_value = self._format_operation_scalar(parsed_payload)
        if not scalar_value:
            return []

        return [f"{default_step} {scalar_value}".strip()]

    def _operation_sort_key(self, raw_value: Any) -> List[int]:
        return [
            int(part) if str(part).isdigit() else 0
            for part in str(raw_value or "").split(".")
        ]

    def _get_operation_sections(self, designation_id: Any) -> List[Dict[str, str]]:
        if not designation_id:
            return []

        rows = self._fetch_all_rows(
            """
            SELECT
                tos.id AS sequence_id,
                tos.operation_index,
                tos.operation_name,
                oc.id AS operation_content_id,
                oc.content AS operation_content,
                eo.id AS equipment_id,
                eo.list AS equipment_list
            FROM control_terms ct
            INNER JOIN tech_operation_sequences tos ON tos.control_term_id = ct.id
            LEFT JOIN operation o ON LOWER(TRIM(o.name)) = LOWER(TRIM(tos.operation_name))
            LEFT JOIN operation_content oc ON oc.id_operation = o.id
            LEFT JOIN equipment_operation eo ON eo.id_operation_content = oc.id
            WHERE ct.designation_id = %s
            ORDER BY ct.id, tos.operation_index, tos.id, oc.id, eo.id
            """,
            (designation_id,),
        )

        sections: Dict[str, Dict[str, Any]] = {}
        section_order: List[str] = []

        for row in rows:
            section_key = str(row.get("sequence_id") or "").strip()
            if not section_key:
                section_key = str(len(section_order) + 1)

            if section_key not in sections:
                sections[section_key] = {
                    "operation_index": str(row.get("operation_index") or "").strip(),
                    "operation_name": str(row.get("operation_name") or "").strip(),
                    "contents": {},
                    "equipment": [],
                }
                section_order.append(section_key)

            section = sections[section_key]
            content_id = row.get("operation_content_id")
            if content_id is not None:
                content_key = str(content_id)
                if content_key not in section["contents"]:
                    section["contents"][content_key] = {
                        "content": row.get("operation_content"),
                        "equipment": [],
                    }

                equipment_value = str(row.get("equipment_list") or "").strip()
                if equipment_value and equipment_value not in section["contents"][content_key]["equipment"]:
                    section["contents"][content_key]["equipment"].append(equipment_value)
            else:
                equipment_value = str(row.get("equipment_list") or "").strip()
                if equipment_value and equipment_value not in section["equipment"]:
                    section["equipment"].append(equipment_value)

        result: List[Dict[str, str]] = []
        for section_key in sorted(section_order, key=lambda key: self._operation_sort_key(sections[key]["operation_index"] or key)):
            section = sections[section_key]
            operation_index = section["operation_index"]
            operation_name = section["operation_name"] or "Операция"
            content_lines: List[str] = []
            equipment_items: List[str] = list(section["equipment"])

            sorted_contents = sorted(
                section["contents"].items(),
                key=lambda item: int(item[0]) if item[0].isdigit() else 0,
            )

            for content_number, (_, content_data) in enumerate(sorted_contents, start=1):
                content_lines.extend(
                    self._render_operation_content(
                        content_data.get("content"),
                        operation_index,
                        content_number,
                    )
                )

                for equipment_value in content_data.get("equipment", []):
                    if equipment_value not in equipment_items:
                        equipment_items.append(equipment_value)

            if not content_lines and operation_name:
                content_lines.append(operation_name)

            section_name = operation_name
            if operation_index and not section_name.startswith(operation_index):
                section_name = f"{operation_index} {section_name}"

            section_value_parts: List[str] = []
            if content_lines:
                section_value_parts.append("\n".join(content_lines))
            if equipment_items:
                section_value_parts.append(
                    "Оборудование и инструмент:\n- " + "\n- ".join(equipment_items)
                )

            result.append(
                {
                    "param_id": operation_index or str(len(result) + 1),
                    "name": section_name,
                    "value": "\n\n".join([part for part in section_value_parts if part]).strip(),
                }
            )

        return result

    def _allocate_operation_param_id(self, proposed_id: str, used_ids: set[str]) -> str:
        normalised = str(proposed_id or "").strip()
        if normalised and all(part.isdigit() for part in normalised.split(".")) and normalised not in used_ids:
            used_ids.add(normalised)
            return normalised

        next_index = 1
        while str(next_index) in used_ids:
            next_index += 1

        allocated_id = str(next_index)
        used_ids.add(allocated_id)
        return allocated_id

    def _fill_operations_block(self, blocks: Dict[int, Dict[str, Any]], designation_id: Any) -> None:
        block = self._ensure_block(blocks, self.OPERATIONS_BLOCK_ID)
        block["name"] = self.BLOCK_LAYOUT[self.OPERATIONS_BLOCK_ID]["name"]
        block["params"] = {}

        used_ids: set[str] = set()
        for section in self._get_operation_sections(designation_id):
            param_id = self._allocate_operation_param_id(section.get("param_id", ""), used_ids)
            self._set_param(
                blocks,
                self.OPERATIONS_BLOCK_ID,
                param_id,
                section.get("name") or f"Операция {param_id}",
                section.get("value") or "",
            )

    def _fill_signatures_block(self, blocks: Dict[int, Dict[str, Any]], engineers_rows: List[Dict[str, Any]]) -> None:
        block = self._ensure_block(blocks, self.SIGNATURES_BLOCK_ID)
        block["name"] = self.BLOCK_LAYOUT[self.SIGNATURES_BLOCK_ID]["name"]
        block["params"] = {}

        developer = engineers_rows[0] if len(engineers_rows) > 0 else {}
        approver = engineers_rows[1] if len(engineers_rows) > 1 else {}

        self._set_param(blocks, self.SIGNATURES_BLOCK_ID, "1", "Разработал - ФИО", developer.get("fio"))
        self._set_param(blocks, self.SIGNATURES_BLOCK_ID, "2", "Разработал - Подпись", "")
        self._set_param(blocks, self.SIGNATURES_BLOCK_ID, "3", "Разработал - Должность, организация", developer.get("organization"))
        self._set_param(blocks, self.SIGNATURES_BLOCK_ID, "4", "Разработал - Уровень квалификации, № удостоверения", developer.get("skill_level"))
        self._set_param(blocks, self.SIGNATURES_BLOCK_ID, "5", "Утвердил - ФИО", approver.get("fio"))
        self._set_param(blocks, self.SIGNATURES_BLOCK_ID, "6", "Утвердил - Подпись", "")
        self._set_param(blocks, self.SIGNATURES_BLOCK_ID, "7", "Утвердил - Должность, организация", approver.get("organization"))
        self._set_param(blocks, self.SIGNATURES_BLOCK_ID, "8", "Утвердил - Уровень квалификации, № удостоверения", approver.get("skill_level"))

    def _preserve_block_values(
        self,
        target_blocks: Dict[int, Dict[str, Any]],
        source: TechCardData | Dict[int, Dict[str, Any]],
        block_id: int,
    ) -> None:
        source_blocks = source.params if isinstance(source, TechCardData) else source
        source_block = source_blocks.get(block_id) or source_blocks.get(str(block_id))
        if not isinstance(source_block, dict):
            return

        source_params = source_block.get("params", {})
        if not isinstance(source_params, dict):
            return

        for param_id, source_param in source_params.items():
            if not isinstance(source_param, dict):
                continue

            target_param = self._get_param(target_blocks, block_id, str(param_id))
            if not isinstance(target_param, dict):
                continue

            source_value = source_param.get("val")
            if source_value not in (None, ""):
                target_param["val"] = self._normalise_value(source_value)

    def _build_operational_card_blocks(
        self,
        element_id: int,
        selected_scheme_id: int | None = None,
        selected_scheme_reference: str | None = None,
    ) -> Dict[int, Dict[str, Any]]:
        blocks = self._build_template_blocks()
        if not self._is_db_available():
            return blocks

        context = self._fetch_element_context(element_id)
        if not context:
            return blocks

        self._fill_header_block(blocks, context)
        scheme_rows, selected_row = self._resolve_selected_scheme_row(
            blocks,
            selected_scheme_id=selected_scheme_id,
            selected_reference=selected_scheme_reference,
        )
        self._fill_object_block(blocks, context)
        self._fill_source_data_block(blocks, context, selected_row)
        self._fill_scheme_block(blocks, scheme_rows, selected_row)
        self._fill_operations_block(blocks, context.get("designation_id"))
        self._fill_signatures_block(blocks, context.get("engineers_rows") or [])
        return blocks

    def get_params_for_type(self, type_id) -> TechCardData:
        _ = type_id
        return self.get_params_for_element(0)

    def get_all_controlled_element_types(self) -> TechCardData:
        tech_card = TechCardData(methodology=self.METHODOLOGY_ID)
        tech_card.type = {1: self.TYPE_NAME}
        return tech_card

    def get_all_objects_by_type_id(self, type_id) -> TechCardData:
        _ = type_id
        tech_card = self._create_card()
        tech_card.params = {
            self.HEADER_BLOCK_ID: {
                "name": self.BLOCK_LAYOUT[self.HEADER_BLOCK_ID]["name"],
                "params": {
                    self.CONTROLLED_ELEMENT_PARAM_ID: {
                        "name": "Наименование объекта",
                        "val": "",
                        "options": self._get_controlled_element_options(),
                        "typeData": "string",
                        "canCreateOption": False,
                        "syncOnSelect": True,
                    }
                },
            }
        }
        return tech_card

    def sync_tech_card(self, tech_card: TechCardData) -> TechCardData:
        element_id = self._get_selected_controlled_element_id(tech_card) or 0
        selected_scheme_id = self._get_param_selected_id(tech_card, self.SCHEME_BLOCK_ID, self.SCHEME_PARAM_ID)
        selected_scheme_reference = self._get_param_value(tech_card, self.SCHEME_BLOCK_ID, self.SCHEME_PARAM_ID)

        rebuilt_blocks = self._build_operational_card_blocks(
            element_id,
            selected_scheme_id=selected_scheme_id,
            selected_scheme_reference=selected_scheme_reference,
        )
        self._preserve_block_values(rebuilt_blocks, tech_card, self.SIGNATURES_BLOCK_ID)

        tech_card.params = rebuilt_blocks
        tech_card.type = self.TYPE_NAME
        tech_card.methodology = self.METHODOLOGY_ID
        return tech_card

    def get_params_for_element(self, element_id: int) -> TechCardData:
        tech_card = self._create_card()
        tech_card.params = self._build_operational_card_blocks(element_id)
        return tech_card
