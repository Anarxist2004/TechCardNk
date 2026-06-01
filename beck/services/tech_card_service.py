from datetime import datetime
from typing import Any

from services.tech_card import TechCardData
from services.PipeLine import PipeLine
from repositories.Interfaces.i_repository import IRepository
from services.Interfaces.i_servise import IServise


class TechCardService(IServise):

    def __init__(self, repos: IRepository, piLine: PipeLine):
        self.repos = repos
        self.pipeLine = piLine

    def _apply_operations_from_db(
        self, card: TechCardData, list_id: int = 1
    ) -> None:
        rows = self.repos.get_operation_params_by_list_id(list_id)
        if not rows:
            return

        block = card.get("4")
        if not isinstance(block, dict):
            return

        block_name = block.get("name")
        if not block_name:
            return

        # Если в БД есть данные, полностью заменяем стандартные операции.
        block["params"] = {}
        insert_pos = 1
        for row in rows:
            val = row.get("val")
            val2 = row.get("val2")
            if val is None and val2 is None:
                continue
            row_id = row.get("id")
            op_name = (
                str(row.get("name_param")).strip()
                if row.get("name_param") is not None and str(row.get("name_param")).strip()
                else f"Операция {row_id}" if row_id is not None else f"Операция {insert_pos}"
            )
            card.insert_param_to_block(
                block_name,
                insert_pos,
                {
                    "name": op_name,
                    "val": val,
                    "val2": val2,
                },
            )
            insert_pos += 1

    def crateTemplateTechCars(self) -> TechCardData:
        card = TechCardData()
        card.set(
            "1",
            {
                "name": "ОПЕРАЦИОННАЯ ТЕХНОЛОГИЧЕСКАЯ КАРТА РАДИОГРАФИЧЕСКОГО КОНТРОЛЯ СВАРНЫХ СОЕДИНЕНИЙ",
                "params": {},
            },
        )
        card.insert_param_to_block(
            card.get("1")["name"],
            1,
            {"name": "Шифр", "val": "ТК-РК 1420х26,4"},
        )
        card.insert_param_to_block(
            card.get("1")["name"],
            2,
            {"name": "Уровень качества", "val": ['A', 'B', 'C']},
        )
        card.insert_param_to_block(
            card.get("1")["name"],
            1,
            {"name": "НАИМЕНОВАНИЕ ОРГАНИЗАЦИИ", "val": None},
        )
        card.insert_param_to_block(
            card.get("1")["name"],
            2,
            {"name": "НОМЕР ЧЕРТЕЖА (ЭСКИЗА)", "val": None},
        )
        card.insert_param_to_block(
            card.get("1")["name"],
            3,
            {"name": "НАИМЕНОВАНИЕ ОБЪЕКТА", "val": None},
        )
        card.insert_param_to_block(
            card.get("1")["name"],
            4,
            {"name": "МЕТОДИКА КОНТРОЛЯ", "val": None},
        )
        card.insert_param_to_block(
            card.get("1")["name"],
            5,
            {"name": "НОРМАТИВНЫЕ ДОКУМЕНТЫ", "val": None},
        )

        card.set("2", {"name": "Объект контроля", "params": {}})
        card.insert_param_to_block(
            card.get("2")["name"],
            1,
            {"name": "Тип сварного соединения", "val": None},
        )

        card.set("3", {"name": "ИСХОДНЫЕ ДАННЫЕ", "params": {}})
        card.insert_param_to_block(
            card.get("3")["name"],
            1,
            {
                "name": "схема просвечивания",
                "val": None,
                "subtitle": "ИСХОДНЫЕ ДАННЫЕ",
                "options": [],
                "typeData": "string",
                "displayMode": None,
            },
        )
        card.insert_param_to_block(
            card.get("3")["name"],
            3,
            {"name": "Радиационная толщина, мм", "val": None},
        )
        card.insert_param_to_block(
            card.get("3")["name"],
            4,
            {"name": "Чувствительность контроля, мм", "val": None},
        )
        card.insert_param_to_block(
            card.get("3")["name"],
            5,
            {"name": "Тип и номер эталона чувствительности", "val": None},
        )
        card.insert_param_to_block(
            card.get("3")["name"],
            6,
            {
                "name": (
                    "Расстояние от ИИИ до поверхности "
                    "контролируемого сварного соединения, мм"
                ),
                "val": None,
            },
        )
        card.insert_param_to_block(
            card.get("3")["name"],
            7,
            {"name": "ИИИ Рентгеновский аппарат", "val": None},
        )
        card.insert_param_to_block(
            card.get("3")["name"],
            8,
            {"name": "Размер фокусного пятна ИИИ, мм", "val": None},
        )
        card.insert_param_to_block(
            card.get("3")["name"],
            9,
            {
                "name": "Напряжение на рентгеновской трубке, не более, кВ",
                "val": None,
            },
        )
        card.insert_param_to_block(
            card.get("3")["name"],
            10,
            {"name": "Тип радиографической пленки D-7 (AGFA)", "val": None},
        )
        card.insert_param_to_block(
            card.get("3")["name"],
            11,
            {"name": "Тип и толщина усиливающего экрана, мм", "val": None},
        )
        card.insert_param_to_block(
            card.get("3")["name"],
            12,
            {"name": "Толщина защитного экрана, мм", "val": None},
        )
        card.insert_param_to_block(
            card.get("3")["name"],
            13,
            {"name": "Количество участков, шт.", "val": None},
        )
        card.insert_param_to_block(
            card.get("3")["name"],
            14,
            {
                "name": "Размеры оценочного участка (ширина × длина), мм",
                "val": None,
            },
        )
        card.insert_param_to_block(
            card.get("3")["name"],
            15,
            {
                "name": "Размеры радиографической пленки (ширина × длина), мм",
                "val": None,
            },
        )

        card.set("4", {"name": "ПЕРЕЧЕНЬ ОПЕРАЦИЙ РК", "params": {}})
        
        
        self._apply_operations_from_db(card, 1)
        card.sort_all_params()
        return card

    def get_template(self) -> TechCardData:
        techCard=self.crateTemplateTechCars()
        self.pipeLine.process(techCard, 0)
        return techCard

    def updateTechCard(self, techCard) -> TechCardData:
        self.pipeLine.process(techCard, 0)
        return techCard

    def _build_default_card_name(self, card_data: dict[str, Any]) -> str:
        snapshot_name = str(card_data.get("cardName") or "").strip()
        if snapshot_name:
            return snapshot_name

        tech_card = card_data.get("techCard", {})
        params = tech_card.get("params", {}) if isinstance(tech_card, dict) else {}
        preferred_names = {
            "РќРђРРњР•РќРћР’РђРќРР• РћР‘РЄР•РљРўРђ",
            "РЁРёС„СЂ",
        }

        for block in params.values():
            if not isinstance(block, dict):
                continue
            for param in block.get("params", {}).values():
                if not isinstance(param, dict):
                    continue
                if param.get("name") not in preferred_names:
                    continue
                value = param.get("val")
                if value is None:
                    continue
                text = str(value).strip()
                if text:
                    return text

        return (
            "РўРµС…РЅРѕР»РѕРіРёС‡РµСЃРєР°СЏ РєР°СЂС‚Р° "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )

    def saveTechCard(
        self,
        name: str,
        card_data: dict[str, Any],
        card_id: int | None = None,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        normalized_name = str(name or "").strip() or self._build_default_card_name(
            card_data
        )
        return self.repos.save_tech_card_snapshot(
            normalized_name,
            card_data,
            card_id,
            user_id,
        )

    def listSavedTechCards(self) -> list[dict[str, Any]]:
        return self.repos.list_saved_tech_cards()

    def listSavedTechCardImages(self) -> list[dict[str, Any]]:
        return self.repos.list_saved_tech_card_images()

    def getSavedTechCard(self, card_id: int) -> dict[str, Any] | None:
        return self.repos.get_saved_tech_card(card_id)


