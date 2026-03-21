import traceback
from typing import Any, Dict, List

from repositories.PostgreDbShablovGazprom import PostgreDbShablovGazprom
from services.tech_card import TechCardData


class PostgreDbShablovGazpromOperational(PostgreDbShablovGazprom):
    METHODOLOGY_ID = 2
    TYPE_NAME = "Контролируемый элемент"

    DISPLAY_MODE_SECTION_HEADER = "section_header"
    DISPLAY_MODE_OPERATIONS_ROW = "operations_row"

    MAIN_INFO_BLOCK_ID = 1
    OBJECT_BLOCK_ID = 2
    SOURCE_DATA_BLOCK_ID = 3
    OPERATIONS_BLOCK_ID = 4

    MAIN_INFO_OBJECT_PARAM_ID = "5"
    JOINT_TYPE_PARAM_ID = "1"
    JOINT_IMAGE_PARAM_ID = "1.1"
    SCHEME_PARAM_ID = "1"
    SCHEME_IMAGE_PARAM_ID = "1.1"

    BLOCK_LAYOUT: Dict[int, Dict[str, Any]] = {
        MAIN_INFO_BLOCK_ID: {
            "name": "Основная информация тех карты",
            "fields": [
                {"id": "1", "name": "ШИФР"},
                {"id": "2", "name": "УРОВЕНЬ КАЧЕСТВА"},
                {"id": "3", "name": "НАИМЕНОВАНИЕ ОРГАНИЗАЦИИ"},
                {"id": "4", "name": "НОМЕР ЧЕРТЕЖА (ЭСКИЗА)"},
                {"id": MAIN_INFO_OBJECT_PARAM_ID, "name": "НАИМЕНОВАНИЕ ОБЪЕКТА"},
                {"id": "6", "name": "МЕТОДИКА КОНТРОЛЯ"},
                {"id": "7", "name": "НОРМАТИВНЫЕ ДОКУМЕНТЫ"},
            ],
        },
        OBJECT_BLOCK_ID: {
            "name": "Объект контроля",
            "fields": [
                {"id": JOINT_TYPE_PARAM_ID, "name": "Тип сварного соединения, тип сварки"},
            ],
        },
        SOURCE_DATA_BLOCK_ID: {
            "name": "ИСХОДНЫЕ ДАННЫЕ",
            "fields": [
                {"id": SCHEME_PARAM_ID, "name": "СХЕМА ПРОСВЕЧИВАНИЯ"},
            ],
        },
        OPERATIONS_BLOCK_ID: {
            "name": "ПЕРЕЧЕНЬ ОПЕРАЦИЙ РК",
            "fields": [],
        },
    }

    OPTIONS_QUERIES: Dict[str, Dict[str, Any]] = {}

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

    def _update_param_metadata(
        self,
        blocks: Dict[int, Dict[str, Any]],
        block_id: int,
        param_id: str,
        **metadata: Any,
    ) -> None:
        param = self._get_param(blocks, block_id, param_id)
        if not isinstance(param, dict):
            return

        for key, value in metadata.items():
            if value is not None:
                param[key] = value

    def _mark_sync_on_select(self, blocks: Dict[int, Dict[str, Any]], block_id: int, param_id: str) -> None:
        self._update_param_metadata(blocks, block_id, param_id, syncOnSelect=True)

    def _mark_read_only(self, blocks: Dict[int, Dict[str, Any]], block_id: int, param_id: str) -> None:
        self._update_param_metadata(blocks, block_id, param_id, readOnly=True)

    def _set_read_only_param(
        self,
        blocks: Dict[int, Dict[str, Any]],
        block_id: int,
        param_id: str,
        name: str,
        value: Any = "",
        display_mode: str | None = None,
        image: Any = None,
    ) -> None:
        self._set_param(
            blocks,
            block_id,
            param_id,
            name,
            value=value,
            image=image,
            display_mode=display_mode,
        )
        self._mark_read_only(blocks, block_id, param_id)

    def _set_section_header(
        self,
        blocks: Dict[int, Dict[str, Any]],
        block_id: int,
        param_id: str,
        name: str,
    ) -> None:
        self._set_read_only_param(
            blocks,
            block_id,
            param_id,
            name,
            value="",
            display_mode=self.DISPLAY_MODE_SECTION_HEADER,
        )

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

    def _get_welded_joint_type_rows(self) -> List[Dict[str, Any]]:
        return self._fetch_all_rows(
            """
            SELECT id, name, "refImg" AS ref_img
            FROM welded_joint_types
            WHERE name IS NOT NULL AND name <> ''
            ORDER BY name, id
            """
        )

    def _get_selected_controlled_element_id(self, source: TechCardData | Dict[int, Dict[str, Any]]) -> int | None:
        selected_id = self._get_param_selected_id(source, self.MAIN_INFO_BLOCK_ID, self.MAIN_INFO_OBJECT_PARAM_ID)
        if selected_id is not None:
            return selected_id

        element_name = self._get_param_value(source, self.MAIN_INFO_BLOCK_ID, self.MAIN_INFO_OBJECT_PARAM_ID)
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

    def _get_selected_welded_joint_type_id(self, source: TechCardData | Dict[int, Dict[str, Any]]) -> int | None:
        selected_id = self._get_param_selected_id(source, self.OBJECT_BLOCK_ID, self.JOINT_TYPE_PARAM_ID)
        if selected_id is not None:
            return selected_id

        joint_type_name = self._get_param_value(source, self.OBJECT_BLOCK_ID, self.JOINT_TYPE_PARAM_ID)
        if not joint_type_name:
            return None

        row = self._fetch_one_row(
            """
            SELECT id
            FROM welded_joint_types
            WHERE name = %s
            ORDER BY id
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
        selected_joint_type_id = self._get_selected_welded_joint_type_id(source)
        if selected_joint_type_id is not None:
            return selected_joint_type_id

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
                wm.name AS welding_method_name,
                wjc.name AS welded_joint_category_name
            FROM designation_params dp
            LEFT JOIN welded_joint_types wjt ON wjt.id = dp.welded_joint_type_id
            LEFT JOIN welding_methods wm ON wm.id = dp.welding_method_id
            LEFT JOIN welded_joint_categories wjc ON wjc.id = dp.welded_joint_category_id
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

        return {
            "element_row": element_row,
            "designation_row": designation_row or {},
            "designation_id": designation_id,
            "designation_params": designation_params or {},
            "dimensions_rows": dimensions_rows,
            "documentation_rows": self._get_documentation_rows(),
        }

    def _fill_main_info_block(self, blocks: Dict[int, Dict[str, Any]], context: Dict[str, Any]) -> None:
        block = self._ensure_block(blocks, self.MAIN_INFO_BLOCK_ID)
        block["name"] = self.BLOCK_LAYOUT[self.MAIN_INFO_BLOCK_ID]["name"]
        block["params"] = {}

        element_row = context.get("element_row") or {}
        designation_params = context.get("designation_params") or {}
        documentation_rows = context.get("documentation_rows") or []
        dimensions_rows = context.get("dimensions_rows") or []
        normative_rows, methodical_rows = self._split_documentation_rows(documentation_rows)
        methodology_parts = [
            self._join_rows(methodical_rows),
            self._join_rows(normative_rows),
        ]
        methodology_value = "; ".join([part for part in methodology_parts if part]) or "Газпром 2"

        self._set_read_only_param(
            blocks,
            self.MAIN_INFO_BLOCK_ID,
            "1",
            "ШИФР",
            self._build_cipher(dimensions_rows),
        )
        self._set_read_only_param(
            blocks,
            self.MAIN_INFO_BLOCK_ID,
            "2",
            "УРОВЕНЬ КАЧЕСТВА",
            self._build_quality_level(designation_params),
        )
        self._set_read_only_param(
            blocks,
            self.MAIN_INFO_BLOCK_ID,
            "3",
            "НАИМЕНОВАНИЕ ОРГАНИЗАЦИИ",
            element_row.get("manufacturer_name"),
        )
        self._set_read_only_param(
            blocks,
            self.MAIN_INFO_BLOCK_ID,
            "4",
            "НОМЕР ЧЕРТЕЖА (ЭСКИЗА)",
            element_row.get("drawing_number_name"),
        )
        self._set_param(
            blocks,
            self.MAIN_INFO_BLOCK_ID,
            self.MAIN_INFO_OBJECT_PARAM_ID,
            "НАИМЕНОВАНИЕ ОБЪЕКТА",
            element_row.get("controlled_element_name"),
            options=self._get_controlled_element_options(),
            selected_id=element_row.get("id"),
        )
        self._mark_sync_on_select(blocks, self.MAIN_INFO_BLOCK_ID, self.MAIN_INFO_OBJECT_PARAM_ID)
        self._set_read_only_param(
            blocks,
            self.MAIN_INFO_BLOCK_ID,
            "6",
            "МЕТОДИКА КОНТРОЛЯ",
            methodology_value,
        )
        self._set_read_only_param(
            blocks,
            self.MAIN_INFO_BLOCK_ID,
            "7",
            "НОРМАТИВНЫЕ ДОКУМЕНТЫ",
            self._join_rows(normative_rows),
        )

    def _resolve_selected_joint_type_row(
        self,
        context: Dict[str, Any],
        selected_joint_type_id: int | None = None,
        selected_joint_type_name: str | None = None,
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any] | None]:
        joint_type_rows = self._get_welded_joint_type_rows()
        selected_row = None

        if selected_joint_type_id is not None:
            selected_row = next(
                (
                    row
                    for row in joint_type_rows
                    if row.get("id") is not None and int(row.get("id")) == selected_joint_type_id
                ),
                None,
            )

        if selected_row is None and selected_joint_type_name:
            selected_row = next(
                (
                    row
                    for row in joint_type_rows
                    if str(row.get("name") or "").strip() == str(selected_joint_type_name).strip()
                ),
                None,
            )

        default_joint_type_id = (context.get("designation_params") or {}).get("welded_joint_type_id")
        if selected_row is None and default_joint_type_id is not None:
            try:
                selected_row = next(
                    (
                        row
                        for row in joint_type_rows
                        if row.get("id") is not None and int(row.get("id")) == int(default_joint_type_id)
                    ),
                    None,
                )
            except (TypeError, ValueError):
                selected_row = None

        if selected_row is None and joint_type_rows:
            selected_row = joint_type_rows[0]

        return joint_type_rows, selected_row

    def _get_params_by_welded_joint_rows(self, welded_joint_type_id: int | None) -> List[Dict[str, Any]]:
        if welded_joint_type_id is None:
            return []

        table_name = "params_by_welded_joint"
        foreign_key_column = self._get_existing_column_name(
            table_name,
            ["welded_joint_type_id", "welded_joint_types_id", "joint_type_id", "type_id"],
        )
        name_column = self._get_existing_column_name(
            table_name,
            ["name", "param_name", "title", "label", "text"],
        )
        value_column = self._get_existing_column_name(
            table_name,
            ["val", "value", "param_value"],
        )
        block_column = self._get_existing_column_name(
            table_name,
            ["block", "block_name", "section", "group_name"],
        )

        if not foreign_key_column or not name_column or not value_column:
            return []

        block_select = f'"{block_column}" AS block_name' if block_column else "NULL AS block_name"
        return self._fetch_all_rows(
            f'''
            SELECT
                id,
                "{name_column}" AS param_name,
                "{value_column}" AS param_value,
                {block_select}
            FROM {table_name}
            WHERE "{foreign_key_column}" = %s
            ORDER BY id
            ''',
            (welded_joint_type_id,),
        )

    def _get_object_block_param_rows(
        self,
        context: Dict[str, Any],
        welded_joint_type_id: int | None,
    ) -> List[Dict[str, Any]]:
        params_rows = self._get_params_by_welded_joint_rows(welded_joint_type_id)
        if params_rows:
            return params_rows

        designation_params = context.get("designation_params") or {}
        default_joint_type_id = designation_params.get("welded_joint_type_id")
        try:
            default_joint_type_id = int(default_joint_type_id) if default_joint_type_id is not None else None
        except (TypeError, ValueError):
            default_joint_type_id = None

        # In the current schema there is no params_by_welded_joint table.
        # Fall back to designation-linked data only for the designation's own
        # welded joint type so we do not show stale dimensions for another type
        # picked manually in the selector.
        if (
            welded_joint_type_id is None
            or default_joint_type_id is None
            or welded_joint_type_id != default_joint_type_id
        ):
            return []

        fallback_rows: List[Dict[str, Any]] = []
        welding_method_name = str(designation_params.get("welding_method_name") or "").strip()
        if welding_method_name:
            fallback_rows.append(
                {
                    "id": "welding_method",
                    "param_name": "Тип сварки",
                    "param_value": welding_method_name,
                    "block_name": None,
                }
            )

        for index, row in enumerate(context.get("dimensions_rows") or [], start=1):
            param_name = str(row.get("text") or "").strip()
            if not param_name:
                continue

            fallback_rows.append(
                {
                    "id": f"dimension_{index}",
                    "param_name": param_name,
                    "param_value": row.get("value"),
                    "block_name": None,
                }
            )

        return fallback_rows

    def _fill_object_block(
        self,
        blocks: Dict[int, Dict[str, Any]],
        context: Dict[str, Any],
        selected_joint_type_id: int | None = None,
        selected_joint_type_name: str | None = None,
    ) -> None:
        block = self._ensure_block(blocks, self.OBJECT_BLOCK_ID)
        block["name"] = self.BLOCK_LAYOUT[self.OBJECT_BLOCK_ID]["name"]
        block["params"] = {}

        joint_type_rows, selected_row = self._resolve_selected_joint_type_row(
            context,
            selected_joint_type_id=selected_joint_type_id,
            selected_joint_type_name=selected_joint_type_name,
        )
        joint_type_options = [
            {"id": str(row.get("id")), "name": str(row.get("name"))}
            for row in joint_type_rows
            if row.get("id") is not None and row.get("name")
        ]
        selected_joint_type_value = str(selected_row.get("name") or "") if selected_row else ""

        self._set_param(
            blocks,
            self.OBJECT_BLOCK_ID,
            self.JOINT_TYPE_PARAM_ID,
            "Тип сварного соединения, тип сварки",
            selected_joint_type_value,
            options=joint_type_options,
            selected_id=selected_row.get("id") if selected_row else None,
        )
        self._mark_sync_on_select(blocks, self.OBJECT_BLOCK_ID, self.JOINT_TYPE_PARAM_ID)

        image_path = self._normalise_res_path(selected_row.get("ref_img") if selected_row else None)
        if image_path:
            self._set_read_only_param(
                blocks,
                self.OBJECT_BLOCK_ID,
                self.JOINT_IMAGE_PARAM_ID,
                "Схема сварного соединения",
                image=image_path,
                display_mode=self.DISPLAY_MODE_IMAGE_FULL,
            )

        selected_joint_type_row_id = selected_row.get("id") if selected_row else None
        try:
            selected_joint_type_row_id = int(selected_joint_type_row_id) if selected_joint_type_row_id is not None else None
        except (TypeError, ValueError):
            selected_joint_type_row_id = None

        params_rows = self._get_object_block_param_rows(context, selected_joint_type_row_id)
        rows_without_group: List[Dict[str, Any]] = []
        grouped_rows: Dict[str, List[Dict[str, Any]]] = {}
        group_order: List[str] = []

        for row in params_rows:
            group_name = str(row.get("block_name") or "").strip()
            if not group_name:
                rows_without_group.append(row)
                continue

            if group_name not in grouped_rows:
                grouped_rows[group_name] = []
                group_order.append(group_name)
            grouped_rows[group_name].append(row)

        next_param_index = 2
        for row in rows_without_group:
            param_name = str(row.get("param_name") or "").strip()
            if not param_name:
                continue
            self._set_read_only_param(
                blocks,
                self.OBJECT_BLOCK_ID,
                str(next_param_index),
                param_name,
                row.get("param_value"),
            )
            next_param_index += 1

        for group_name in group_order:
            group_param_id = str(next_param_index)
            self._set_section_header(
                blocks,
                self.OBJECT_BLOCK_ID,
                group_param_id,
                group_name,
            )
            next_param_index += 1

            for row_index, row in enumerate(grouped_rows[group_name], start=1):
                param_name = str(row.get("param_name") or "").strip()
                if not param_name:
                    continue
                self._set_read_only_param(
                    blocks,
                    self.OBJECT_BLOCK_ID,
                    f"{group_param_id}.{row_index}",
                    param_name,
                    row.get("param_value"),
                )

    def _resolve_selected_scheme_row(
        self,
        source: TechCardData | Dict[int, Dict[str, Any]],
        selected_scheme_id: int | None = None,
        selected_reference: str | None = None,
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any] | None]:
        scheme_rows = self._get_transmission_scheme_rows(source)
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

    def _fill_source_data_block(
        self,
        blocks: Dict[int, Dict[str, Any]],
        selected_scheme_id: int | None = None,
        selected_scheme_reference: str | None = None,
    ) -> None:
        block = self._ensure_block(blocks, self.SOURCE_DATA_BLOCK_ID)
        block["name"] = self.BLOCK_LAYOUT[self.SOURCE_DATA_BLOCK_ID]["name"]
        block["params"] = {}

        scheme_rows, selected_row = self._resolve_selected_scheme_row(
            blocks,
            selected_scheme_id=selected_scheme_id,
            selected_scheme_reference=selected_scheme_reference,
        )
        scheme_options = [
            {"id": str(row.get("id")), "name": str(row.get("reference"))}
            for row in scheme_rows
            if row.get("id") is not None and row.get("reference")
        ]
        selected_scheme_value = str(selected_row.get("reference") or "") if selected_row else ""

        self._set_param(
            blocks,
            self.SOURCE_DATA_BLOCK_ID,
            self.SCHEME_PARAM_ID,
            "СХЕМА ПРОСВЕЧИВАНИЯ",
            selected_scheme_value,
            options=scheme_options,
            selected_id=selected_row.get("id") if selected_row else None,
        )
        self._mark_sync_on_select(blocks, self.SOURCE_DATA_BLOCK_ID, self.SCHEME_PARAM_ID)

        image_path = self._get_transmission_scheme_image_path(selected_row)
        if image_path:
            self._set_read_only_param(
                blocks,
                self.SOURCE_DATA_BLOCK_ID,
                self.SCHEME_IMAGE_PARAM_ID,
                "Схема просвечивания",
                image=image_path,
                display_mode=self.DISPLAY_MODE_IMAGE_FULL,
            )

        selected_scheme_row_id = selected_row.get("id") if selected_row else None
        if selected_scheme_row_id is None:
            return

        scheme_params_rows = self._fetch_all_rows(
            """
            SELECT name, val
            FROM params_transmission_scheme
            WHERE transmission_schemes_id = %s
            ORDER BY id
            """,
            (selected_scheme_row_id,),
        )

        next_param_index = 2
        for row in scheme_params_rows:
            param_name = str(row.get("name") or "").strip()
            if not param_name:
                continue
            self._set_read_only_param(
                blocks,
                self.SOURCE_DATA_BLOCK_ID,
                str(next_param_index),
                param_name,
                row.get("val"),
            )
            next_param_index += 1

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

    def _resolve_operation_name(self, row: Dict[str, Any]) -> str:
        candidates = (
            row.get("operation_table_name"),
            row.get("sequence_operation_name"),
        )

        for candidate in candidates:
            normalised = str(candidate or "").strip()
            if normalised:
                return normalised

        return "Операция"

    def _append_unique_text(self, target: List[str], value: Any) -> None:
        normalised = str(value or "").strip()
        if normalised and normalised not in target:
            target.append(normalised)

    def _fetch_operation_order_rows(self, designation_id: Any) -> List[Dict[str, Any]]:
        if designation_id:
            rows = self._fetch_all_rows(
                """
                SELECT
                    tos.id AS sequence_id,
                    tos.operation_index,
                    tos.operation_name AS sequence_operation_name,
                    o.id AS operation_id,
                    o.name AS operation_table_name
                FROM control_terms ct
                INNER JOIN tech_operation_sequences tos ON tos.control_term_id = ct.id
                LEFT JOIN operation o ON LOWER(TRIM(o.name)) = LOWER(TRIM(tos.operation_name))
                WHERE ct.designation_id = %s
                ORDER BY ct.id, tos.operation_index, tos.id, o.id
                """,
                (designation_id,),
            )
            if rows:
                return rows

        return self._fetch_all_rows(
            """
            SELECT
                NULL::integer AS sequence_id,
                NULL::text AS operation_index,
                name AS sequence_operation_name,
                id AS operation_id,
                name AS operation_table_name
            FROM operation
            ORDER BY id
            """
        )

    def _fetch_operation_content_rows(self, operation_id: int | None) -> List[Dict[str, Any]]:
        if operation_id is None:
            return []

        return self._fetch_all_rows(
            """
            SELECT id, content
            FROM operation_content
            WHERE id_operation = %s
            ORDER BY id
            """,
            (operation_id,),
        )

    def _fetch_equipment_rows(self, operation_content_id: int | None) -> List[Dict[str, Any]]:
        if operation_content_id is None:
            return []

        return self._fetch_all_rows(
            """
            SELECT id, list AS equipment_list
            FROM equipment_operation
            WHERE id_operation_content = %s
            ORDER BY id
            """,
            (operation_content_id,),
        )

    def _get_operation_rows(self, designation_id: Any) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        ordered_rows = self._fetch_operation_order_rows(designation_id)

        for fallback_index, row in enumerate(ordered_rows, start=1):
            operation_index = str(row.get("operation_index") or "").strip()
            operation_name = self._resolve_operation_name(row)

            operation_id = row.get("operation_id")
            try:
                operation_id = int(operation_id) if operation_id is not None else None
            except (TypeError, ValueError):
                operation_id = None

            content_lines: List[str] = []
            equipment_items: List[str] = []
            content_rows = self._fetch_operation_content_rows(operation_id)

            for content_index, content_row in enumerate(content_rows, start=1):
                content_lines.extend(
                    self._render_operation_content(
                        content_row.get("content"),
                        operation_index,
                        content_index,
                    )
                )

                content_row_id = content_row.get("id")
                try:
                    content_row_id = int(content_row_id) if content_row_id is not None else None
                except (TypeError, ValueError):
                    content_row_id = None

                for equipment_row in self._fetch_equipment_rows(content_row_id):
                    self._append_unique_text(equipment_items, equipment_row.get("equipment_list"))

            section_name = operation_name
            if operation_index and section_name and not section_name.startswith(operation_index):
                section_name = f"{operation_index} {section_name}"

            result.append(
                {
                    "param_id": operation_index or str(fallback_index),
                    "name": section_name or f"Операция {fallback_index}",
                    "content": "\n".join(content_lines).strip(),
                    "equipment": "\n".join(f"- {item}" for item in equipment_items).strip(),
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
        for row in self._get_operation_rows(designation_id):
            param_id = self._allocate_operation_param_id(row.get("param_id", ""), used_ids)
            self._set_param(
                blocks,
                self.OPERATIONS_BLOCK_ID,
                param_id,
                row.get("name") or f"Операция {param_id}",
                value={
                    "content": row.get("content") or "",
                    "equipment": row.get("equipment") or "",
                },
                display_mode=self.DISPLAY_MODE_OPERATIONS_ROW,
            )
            self._mark_read_only(blocks, self.OPERATIONS_BLOCK_ID, param_id)

    def _build_operational_card_blocks_safe(
        self,
        element_id: int,
        selected_joint_type_id: int | None = None,
        selected_joint_type_name: str | None = None,
        selected_scheme_id: int | None = None,
        selected_scheme_reference: str | None = None,
    ) -> Dict[int, Dict[str, Any]]:
        try:
            return self._build_operational_card_blocks(
                element_id,
                selected_joint_type_id=selected_joint_type_id,
                selected_joint_type_name=selected_joint_type_name,
                selected_scheme_id=selected_scheme_id,
                selected_scheme_reference=selected_scheme_reference,
            )
        except Exception as error:
            print(
                "[Gazprom2] Failed to build operational tech card: "
                f"element_id={element_id}, "
                f"selected_joint_type_id={selected_joint_type_id}, "
                f"selected_scheme_id={selected_scheme_id}. "
                f"Error: {error}"
            )
            traceback.print_exc()
            return self._build_template_blocks()

    def _build_operational_card_blocks(
        self,
        element_id: int,
        selected_joint_type_id: int | None = None,
        selected_joint_type_name: str | None = None,
        selected_scheme_id: int | None = None,
        selected_scheme_reference: str | None = None,
    ) -> Dict[int, Dict[str, Any]]:
        blocks = self._build_template_blocks()
        if not self._is_db_available():
            return blocks

        context = self._fetch_element_context(element_id)
        self._fill_main_info_block(blocks, context)
        self._fill_object_block(
            blocks,
            context,
            selected_joint_type_id=selected_joint_type_id,
            selected_joint_type_name=selected_joint_type_name,
        )
        self._fill_source_data_block(
            blocks,
            selected_scheme_id=selected_scheme_id,
            selected_scheme_reference=selected_scheme_reference,
        )
        self._fill_operations_block(blocks, context.get("designation_id"))
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
            self.MAIN_INFO_BLOCK_ID: {
                "name": self.BLOCK_LAYOUT[self.MAIN_INFO_BLOCK_ID]["name"],
                "params": {
                    self.MAIN_INFO_OBJECT_PARAM_ID: {
                        "name": "НАИМЕНОВАНИЕ ОБЪЕКТА",
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
        selected_joint_type_id = self._get_param_selected_id(tech_card, self.OBJECT_BLOCK_ID, self.JOINT_TYPE_PARAM_ID)
        selected_joint_type_name = self._get_param_value(tech_card, self.OBJECT_BLOCK_ID, self.JOINT_TYPE_PARAM_ID)
        selected_scheme_id = self._get_param_selected_id(tech_card, self.SOURCE_DATA_BLOCK_ID, self.SCHEME_PARAM_ID)
        selected_scheme_reference = self._get_param_value(tech_card, self.SOURCE_DATA_BLOCK_ID, self.SCHEME_PARAM_ID)

        tech_card.params = self._build_operational_card_blocks_safe(
            element_id,
            selected_joint_type_id=selected_joint_type_id,
            selected_joint_type_name=selected_joint_type_name,
            selected_scheme_id=selected_scheme_id,
            selected_scheme_reference=selected_scheme_reference,
        )
        tech_card.type = self.TYPE_NAME
        tech_card.methodology = self.METHODOLOGY_ID
        return tech_card

    def get_params_for_element(self, element_id: int) -> TechCardData:
        tech_card = self._create_card()
        tech_card.params = self._build_operational_card_blocks_safe(element_id)
        return tech_card
