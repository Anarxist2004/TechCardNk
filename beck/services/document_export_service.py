import base64
import re
import struct
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from services.tech_card import TechCardData


class DocumentExportService:
    DOCX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    DEFAULT_FILENAME = "tech-card.docx"
    DEFAULT_TITLE = "Технологическая карта"

    def __init__(self, res_dir: Path | None = None):
        self.res_dir = Path(res_dir) if res_dir else Path(__file__).resolve().parent.parent / "res"

    def export_docx(self, tech_card: TechCardData, payload: dict | None = None) -> dict[str, Any]:
        export_payload = payload if isinstance(payload, dict) else {}
        metadata = dict(export_payload.get("metadata") or {})
        custom_fields = self._normalise_custom_fields(export_payload.get("customFields"))
        uploaded_images = self._normalise_uploaded_images(export_payload.get("uploadedImages"))

        body_elements, image_relationships, media_entries = self._build_document_body(
            tech_card,
            metadata,
            custom_fields,
            uploaded_images,
        )
        docx_bytes = self._build_docx_package(
            body_elements=body_elements,
            image_relationships=image_relationships,
            media_entries=media_entries,
            title=str(metadata.get("title") or self.DEFAULT_TITLE),
        )

        return {
            "filename": self._build_filename(metadata),
            "content_type": self.DOCX_CONTENT_TYPE,
            "content": docx_bytes,
        }

    def _build_filename(self, metadata: dict[str, Any]) -> str:
        parts = [
            metadata.get("methodologyName"),
            metadata.get("objectName"),
            metadata.get("elementName"),
        ]
        safe_parts = [
            self._slugify(part)
            for part in parts
            if isinstance(part, str) and part.strip()
        ]

        if not safe_parts:
            return self.DEFAULT_FILENAME

        return f"tech-card-{'-'.join(safe_parts[:3])}.docx"

    def _build_document_body(
        self,
        tech_card: TechCardData,
        metadata: dict[str, Any],
        custom_fields: dict[str, list[dict[str, str]]],
        uploaded_images: dict[str, list[dict[str, str]]],
    ) -> tuple[list[str], list[dict[str, str]], list[dict[str, Any]]]:
        body_elements: list[str] = []
        image_relationships: list[dict[str, str]] = []
        media_entries: list[dict[str, Any]] = []

        image_counter = 1
        relation_counter = 2
        doc_pr_id = 1

        def register_image(source: str, name: str, full_width: bool = False) -> str | None:
            nonlocal image_counter, relation_counter, doc_pr_id

            image_info = self._resolve_image(source)
            if not image_info:
                return None

            rel_id = f"rId{relation_counter}"
            relation_counter += 1
            file_name = f"image{image_counter}.{image_info['extension']}"
            image_counter += 1

            media_entries.append(
                {
                    "path": f"word/media/{file_name}",
                    "content": image_info["bytes"],
                }
            )
            image_relationships.append(
                {
                    "id": rel_id,
                    "target": f"media/{file_name}",
                }
            )

            width_px, height_px = self._get_image_dimensions(image_info["bytes"], image_info["extension"])
            extent_cx, extent_cy = self._calculate_image_extent(width_px, height_px, full_width=full_width)
            image_paragraph = self._image_paragraph(
                rel_id=rel_id,
                name=name or f"Изображение {image_counter - 1}",
                extent_cx=extent_cx,
                extent_cy=extent_cy,
                doc_pr_id=doc_pr_id,
            )
            doc_pr_id += 1
            return image_paragraph

        title = str(metadata.get("title") or self.DEFAULT_TITLE)
        body_elements.append(self._paragraph([(title, {"bold": True})], style="Title"))

        metadata_rows = [
            ("Методика", metadata.get("methodologyName")),
            ("Объект контроля", metadata.get("objectName")),
            ("Элемент контроля", metadata.get("elementName")),
        ]
        for label, value in metadata_rows:
            if not isinstance(value, str) or not value.strip():
                continue
            body_elements.append(
                self._paragraph(
                    [
                        (f"{label}: ", {"bold": True}),
                        (value.strip(), {}),
                    ]
                )
            )

        body_elements.append(
            self._paragraph(
                [
                    ("Дата экспорта: ", {"bold": True}),
                    (datetime.now().strftime("%d.%m.%Y %H:%M"), {}),
                ]
            )
        )

        for block_id, block_data in self._iter_blocks(tech_card):
            block_name = str(block_data.get("name") or f"Блок {block_id}")
            body_elements.append(
                self._paragraph(
                    [(f"{block_id}. {block_name}", {"bold": True})],
                    style="Heading1",
                )
            )

            block_items_count = 0
            for param_id, param_data in self._iter_params(block_data.get("params") or {}):
                param_number = f"{block_id}.{param_id}"
                param_name = str(param_data.get("name") or "").strip()
                display_mode = param_data.get("displayMode")
                image_source = self._get_param_image_source(param_data)

                if image_source:
                    if display_mode != "image_full":
                        image_caption = param_name or param_number
                        body_elements.append(
                            self._paragraph(
                                [
                                    (param_number, {"bold": True}),
                                    (" ", {}),
                                    (image_caption, {}),
                                ]
                            )
                        )
                    image_paragraph = register_image(
                        image_source,
                        name=param_name or param_number,
                        full_width=display_mode == "image_full",
                    )
                    if image_paragraph:
                        body_elements.append(image_paragraph)
                    else:
                        body_elements.append(
                            self._paragraph(
                                [
                                    ("Изображение: ", {"bold": True}),
                                    (param_name or param_number, {}),
                                ]
                            )
                        )
                    block_items_count += 1
                    continue

                display_value = self._get_param_display_value(param_data)
                if display_value == "":
                    continue

                if display_mode == "number_only":
                    runs = [
                        (param_number, {"bold": True}),
                        (" ", {}),
                        (display_value, {}),
                    ]
                else:
                    runs = [
                        (param_number, {"bold": True}),
                        (" ", {}),
                    ]
                    if param_name:
                        runs.extend(
                            [
                                (param_name, {"bold": True}),
                                (": ", {}),
                            ]
                        )
                    runs.append((display_value, {}))

                body_elements.append(self._paragraph(runs))
                block_items_count += 1

            extra_fields = custom_fields.get(str(block_id), [])
            if extra_fields:
                body_elements.append(self._paragraph([("Дополнительные поля", {"bold": True})], style="Heading2"))
                for field in extra_fields:
                    field_name = field.get("name") or "Дополнительное поле"
                    field_value = field.get("value") or ""
                    body_elements.append(
                        self._paragraph(
                            [
                                (field_name, {"bold": True}),
                                (": ", {}),
                                (field_value, {}),
                            ]
                        )
                    )
                    block_items_count += 1

            extra_images = uploaded_images.get(str(block_id), [])
            if extra_images:
                body_elements.append(self._paragraph([("Дополнительные изображения", {"bold": True})], style="Heading2"))
                for image in extra_images:
                    image_name = image.get("name") or "Изображение"
                    body_elements.append(self._paragraph([(image_name, {"italic": True})]))
                    image_paragraph = register_image(image.get("preview", ""), image_name, full_width=False)
                    if image_paragraph:
                        body_elements.append(image_paragraph)
                    else:
                        body_elements.append(self._paragraph([("Не удалось встроить изображение.", {"italic": True})]))
                    block_items_count += 1

            if block_items_count == 0:
                body_elements.append(self._paragraph([("Нет заполненных данных.", {"italic": True})]))

        return body_elements, image_relationships, media_entries

    def _build_docx_package(
        self,
        body_elements: list[str],
        image_relationships: list[dict[str, str]],
        media_entries: list[dict[str, Any]],
        title: str,
    ) -> bytes:
        buffer = BytesIO()
        with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", self._content_types_xml())
            archive.writestr("_rels/.rels", self._root_relationships_xml())
            archive.writestr("word/document.xml", self._document_xml(body_elements))
            archive.writestr("word/_rels/document.xml.rels", self._document_relationships_xml(image_relationships))
            archive.writestr("word/styles.xml", self._styles_xml())
            archive.writestr("docProps/app.xml", self._app_xml())
            archive.writestr("docProps/core.xml", self._core_xml(title))

            for media_entry in media_entries:
                archive.writestr(media_entry["path"], media_entry["content"])

        return buffer.getvalue()

    def _document_xml(self, body_elements: list[str]) -> str:
        body_xml = "".join(body_elements)
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document '
            'xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
            'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
            'xmlns:o="urn:schemas-microsoft-com:office:office" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
            'xmlns:v="urn:schemas-microsoft-com:vml" '
            'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
            'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
            'xmlns:w10="urn:schemas-microsoft-com:office:word" '
            'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
            'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" '
            'xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" '
            'xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" '
            'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
            'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
            'mc:Ignorable="w14 wp14">'
            "<w:body>"
            f"{body_xml}"
            '<w:sectPr>'
            '<w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="1134" w:right="850" w:bottom="1134" w:left="850" w:header="708" w:footer="708" w:gutter="0"/>'
            "</w:sectPr>"
            "</w:body>"
            "</w:document>"
        )

    def _content_types_xml(self) -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Default Extension="png" ContentType="image/png"/>'
            '<Default Extension="jpg" ContentType="image/jpeg"/>'
            '<Default Extension="jpeg" ContentType="image/jpeg"/>'
            '<Default Extension="gif" ContentType="image/gif"/>'
            '<Default Extension="bmp" ContentType="image/bmp"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
            '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
            '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
            "</Types>"
        )

    def _root_relationships_xml(self) -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
            "</Relationships>"
        )

    def _document_relationships_xml(self, image_relationships: list[dict[str, str]]) -> str:
        image_xml = "".join(
            (
                '<Relationship '
                f'Id="{item["id"]}" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                f'Target="{item["target"]}"/>'
            )
            for item in image_relationships
        )
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            f"{image_xml}"
            "</Relationships>"
        )

    def _styles_xml(self) -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
            '<w:name w:val="Normal"/>'
            '<w:qFormat/>'
            '<w:rPr><w:sz w:val="22"/></w:rPr>'
            "</w:style>"
            '<w:style w:type="paragraph" w:styleId="Title">'
            '<w:name w:val="Title"/>'
            '<w:basedOn w:val="Normal"/>'
            '<w:qFormat/>'
            '<w:pPr><w:spacing w:before="0" w:after="260"/></w:pPr>'
            '<w:rPr><w:b/><w:sz w:val="30"/></w:rPr>'
            "</w:style>"
            '<w:style w:type="paragraph" w:styleId="Heading1">'
            '<w:name w:val="Heading 1"/>'
            '<w:basedOn w:val="Normal"/>'
            '<w:qFormat/>'
            '<w:pPr><w:spacing w:before="260" w:after="140"/></w:pPr>'
            '<w:rPr><w:b/><w:sz w:val="26"/></w:rPr>'
            "</w:style>"
            '<w:style w:type="paragraph" w:styleId="Heading2">'
            '<w:name w:val="Heading 2"/>'
            '<w:basedOn w:val="Normal"/>'
            '<w:qFormat/>'
            '<w:pPr><w:spacing w:before="160" w:after="100"/></w:pPr>'
            '<w:rPr><w:b/><w:sz w:val="24"/></w:rPr>'
            "</w:style>"
            "</w:styles>"
        )

    def _app_xml(self) -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
            'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
            "<Application>Codex TechCard Export</Application>"
            "</Properties>"
        )

    def _core_xml(self, title: str) -> str:
        created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" '
            'xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:dcmitype="http://purl.org/dc/dcmitype/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f"<dc:title>{escape(title or self.DEFAULT_TITLE)}</dc:title>"
            "<dc:creator>Codex</dc:creator>"
            "<cp:lastModifiedBy>Codex</cp:lastModifiedBy>"
            f'<dcterms:created xsi:type="dcterms:W3CDTF">{created_at}</dcterms:created>'
            f'<dcterms:modified xsi:type="dcterms:W3CDTF">{created_at}</dcterms:modified>'
            "</cp:coreProperties>"
        )

    def _paragraph(
        self,
        runs: list[tuple[str, dict[str, bool]]],
        style: str | None = None,
    ) -> str:
        paragraph_props = []
        if style:
            paragraph_props.append(f'<w:pStyle w:val="{escape(style)}"/>')

        runs_xml = "".join(self._run(text, **(run_props or {})) for text, run_props in runs if text is not None)
        if not runs_xml:
            runs_xml = self._run("")

        if paragraph_props:
            return f"<w:p><w:pPr>{''.join(paragraph_props)}</w:pPr>{runs_xml}</w:p>"
        return f"<w:p>{runs_xml}</w:p>"

    def _run(self, text: str = "", bold: bool = False, italic: bool = False) -> str:
        run_props = []
        if bold:
            run_props.append("<w:b/>")
        if italic:
            run_props.append("<w:i/>")

        lines = str(text or "").splitlines() or [""]
        text_xml_parts = []
        for index, line in enumerate(lines):
            if index > 0:
                text_xml_parts.append("<w:br/>")
            text_xml_parts.append(f'<w:t xml:space="preserve">{escape(line)}</w:t>')

        if run_props:
            return f"<w:r><w:rPr>{''.join(run_props)}</w:rPr>{''.join(text_xml_parts)}</w:r>"
        return f"<w:r>{''.join(text_xml_parts)}</w:r>"

    def _image_paragraph(
        self,
        rel_id: str,
        name: str,
        extent_cx: int,
        extent_cy: int,
        doc_pr_id: int,
    ) -> str:
        safe_name = escape(name or f"Image {doc_pr_id}")
        return (
            "<w:p>"
            "<w:r>"
            "<w:drawing>"
            '<wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="{extent_cx}" cy="{extent_cy}"/>'
            f'<wp:docPr id="{doc_pr_id}" name="{safe_name}"/>'
            "<wp:cNvGraphicFramePr/>"
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            "<pic:nvPicPr>"
            f'<pic:cNvPr id="{doc_pr_id}" name="{safe_name}"/>'
            "<pic:cNvPicPr/>"
            "</pic:nvPicPr>"
            "<pic:blipFill>"
            f'<a:blip r:embed="{rel_id}"/>'
            "<a:stretch><a:fillRect/></a:stretch>"
            "</pic:blipFill>"
            "<pic:spPr>"
            "<a:xfrm>"
            '<a:off x="0" y="0"/>'
            f'<a:ext cx="{extent_cx}" cy="{extent_cy}"/>'
            "</a:xfrm>"
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            "</pic:spPr>"
            "</pic:pic>"
            "</a:graphicData>"
            "</a:graphic>"
            "</wp:inline>"
            "</w:drawing>"
            "</w:r>"
            "</w:p>"
        )

    def _iter_blocks(self, tech_card: TechCardData):
        return sorted((tech_card.params or {}).items(), key=lambda item: self._sort_key(item[0]))

    def _iter_params(self, params: dict[str, Any]):
        return sorted((params or {}).items(), key=lambda item: self._sort_key(item[0]))

    def _sort_key(self, raw_key: Any) -> tuple[int, ...]:
        if isinstance(raw_key, int):
            return (raw_key,)

        key = str(raw_key)
        try:
            return tuple(int(part) for part in key.split("."))
        except ValueError:
            return (10**9,)

    def _get_param_display_value(self, param_data: dict[str, Any]) -> str:
        value = param_data.get("val")

        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, (int, float, bool)):
            return str(value)
        if isinstance(value, list):
            values = [self._stringify_value(item) for item in value]
            values = [item for item in values if item]
            return ", ".join(values)
        if isinstance(value, dict):
            if value.get("name") is not None:
                return str(value.get("name")).strip()
            if value.get("value") is not None:
                return str(value.get("value")).strip()
            lines = []
            for nested_key, nested_value in value.items():
                if nested_key == "image":
                    continue
                nested_text = self._stringify_value(nested_value)
                if nested_text:
                    lines.append(f"{nested_key}: {nested_text}")
            return "\n".join(lines).strip()

        return str(value).strip()

    def _stringify_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, dict):
            if value.get("name") is not None:
                return str(value.get("name")).strip()
            if value.get("value") is not None:
                return str(value.get("value")).strip()
            parts = []
            for nested_key, nested_value in value.items():
                nested_text = self._stringify_value(nested_value)
                if nested_text:
                    parts.append(f"{nested_key}: {nested_text}")
            return "; ".join(parts)
        if isinstance(value, list):
            parts = [self._stringify_value(item) for item in value]
            return ", ".join(item for item in parts if item)
        return str(value).strip()

    def _get_param_image_source(self, param_data: dict[str, Any]) -> str | None:
        if param_data.get("image"):
            return str(param_data.get("image"))

        value = param_data.get("val")
        if isinstance(value, dict) and value.get("image"):
            return str(value.get("image"))

        return None

    def _normalise_custom_fields(self, raw_custom_fields: Any) -> dict[str, list[dict[str, str]]]:
        if not isinstance(raw_custom_fields, dict):
            return {}

        normalized: dict[str, list[dict[str, str]]] = {}
        for block_id, fields in raw_custom_fields.items():
            if not isinstance(fields, list):
                continue

            block_fields = []
            for field in fields:
                if not isinstance(field, dict):
                    continue
                name = str(field.get("name") or "").strip()
                value = str(field.get("value") or "").strip()
                if not name and not value:
                    continue
                block_fields.append({"name": name, "value": value})

            if block_fields:
                normalized[str(block_id)] = block_fields

        return normalized

    def _normalise_uploaded_images(self, raw_uploaded_images: Any) -> dict[str, list[dict[str, str]]]:
        if not isinstance(raw_uploaded_images, dict):
            return {}

        normalized: dict[str, list[dict[str, str]]] = {}
        for block_id, images in raw_uploaded_images.items():
            if not isinstance(images, list):
                continue

            block_images = []
            for image in images:
                if not isinstance(image, dict):
                    continue
                preview = str(image.get("preview") or "").strip()
                if not preview:
                    continue
                block_images.append(
                    {
                        "name": str(image.get("name") or "Изображение").strip(),
                        "preview": preview,
                    }
                )

            if block_images:
                normalized[str(block_id)] = block_images

        return normalized

    def _resolve_image(self, source: str) -> dict[str, Any] | None:
        raw_source = str(source or "").strip()
        if not raw_source:
            return None

        if raw_source.startswith("data:image/"):
            header, _, encoded = raw_source.partition(",")
            match = re.search(r"data:image/([a-zA-Z0-9+]+);base64", header)
            extension = (match.group(1) if match else "png").lower().replace("jpeg", "jpg")
            try:
                return {
                    "bytes": base64.b64decode(encoded),
                    "extension": extension,
                }
            except Exception:
                return None

        if raw_source.startswith("/res/") or raw_source.startswith("res/"):
            relative_path = raw_source.replace("\\", "/").lstrip("/")
            if relative_path.startswith("res/"):
                relative_path = relative_path[4:]
            image_path = self.res_dir / relative_path
            if image_path.exists():
                return {
                    "bytes": image_path.read_bytes(),
                    "extension": image_path.suffix.lstrip(".").lower() or "png",
                }

        local_path = Path(raw_source)
        if local_path.exists() and local_path.is_file():
            return {
                "bytes": local_path.read_bytes(),
                "extension": local_path.suffix.lstrip(".").lower() or "png",
            }

        if self._looks_like_base64(raw_source):
            try:
                return {
                    "bytes": base64.b64decode(raw_source),
                    "extension": "png",
                }
            except Exception:
                return None

        return None

    def _looks_like_base64(self, value: str) -> bool:
        if "/" in value or "\\" in value or " " in value:
            return False
        return len(value) > 64 and re.fullmatch(r"[A-Za-z0-9+/=]+", value) is not None

    def _get_image_dimensions(self, image_bytes: bytes, extension: str) -> tuple[int, int]:
        extension = (extension or "").lower()

        try:
            if extension == "png" and len(image_bytes) >= 24:
                width, height = struct.unpack(">II", image_bytes[16:24])
                return int(width), int(height)

            if extension in {"jpg", "jpeg"}:
                return self._read_jpeg_size(image_bytes)

            if extension == "gif" and len(image_bytes) >= 10:
                width, height = struct.unpack("<HH", image_bytes[6:10])
                return int(width), int(height)

            if extension == "bmp" and len(image_bytes) >= 26:
                width, height = struct.unpack("<II", image_bytes[18:26])
                return int(width), int(height)
        except Exception:
            pass

        return 1024, 768

    def _read_jpeg_size(self, image_bytes: bytes) -> tuple[int, int]:
        index = 2
        size = len(image_bytes)

        while index + 9 < size:
            if image_bytes[index] != 0xFF:
                index += 1
                continue

            marker = image_bytes[index + 1]
            index += 2

            if marker in {0xD8, 0xD9}:
                continue

            if index + 2 > size:
                break
            segment_length = struct.unpack(">H", image_bytes[index:index + 2])[0]
            if segment_length < 2:
                break

            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                if index + 7 > size:
                    break
                height, width = struct.unpack(">HH", image_bytes[index + 3:index + 7])
                return int(width), int(height)

            index += segment_length

        return 1024, 768

    def _calculate_image_extent(self, width_px: int, height_px: int, full_width: bool = False) -> tuple[int, int]:
        width_px = max(int(width_px or 0), 1)
        height_px = max(int(height_px or 0), 1)

        max_width_inches = 6.7 if full_width else 5.8
        max_height_inches = 8.6 if full_width else 5.6
        width_inches = width_px / 96
        height_inches = height_px / 96

        scale = min(max_width_inches / width_inches, max_height_inches / height_inches, 1.0)
        scaled_width_inches = width_inches * scale
        scaled_height_inches = height_inches * scale

        return int(scaled_width_inches * 914400), int(scaled_height_inches * 914400)

    def _slugify(self, value: str) -> str:
        normalized = re.sub(r"\s+", "-", str(value).strip().lower())
        normalized = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁ_-]", "", normalized)
        normalized = normalized.strip("-_")
        return normalized or "tech-card"
