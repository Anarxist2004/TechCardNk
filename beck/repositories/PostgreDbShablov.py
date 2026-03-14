from interfaces.i_repository import IRepository
from services.tech_card import TechCardData
from services.tech_card import TypeObjectControl
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

from typing import List, Dict, Any

class PostgreDbShablov(IRepository[TechCardData]):
    def __init__(self, dsn: str):
        self._cards: List[TechCardData] = []
        try:
            self.conn = psycopg2.connect(dsn)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("Подключение к базе успешно")
        except psycopg2.Error as e:
            print("Ошибка при подключении к базе:", e)
            self.conn = None
            self.cursor = None

    def add(self, entity: TechCardData) -> None:
        self._cards.append(entity)

    def update(self, entity: TechCardData) -> None:
        for i, card in enumerate(self._cards):
            if getattr(card, "id", None) == getattr(entity, "id", None):
                self._cards[i] = entity
                return

    def delete(self, entity: TechCardData) -> None:
        entity_id = getattr(entity, "id", None)
        self._cards = [c for c in self._cards if getattr(c, "id", None) != entity_id]

    def get_by_id(self, id: int) -> Optional[TechCardData]:
        for card in self._cards:
            if getattr(card, "id", None) == id:
                return card
        return None

    def list_all(self) -> List[TechCardData]:
        return self._cards.copy()

    def close(self) -> None:
        """Закрытие подключения к БД."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def get_params_for_type(self, type_id):#получение параметров всех типов контролирующего элемента
        pass


    def get_all_controlled_element_types(self)->TechCardData:#получение всех типов контролируемых эементов
        if not self.conn or not self.cursor:
            return TechCardData()
        try:

            all_data = self.get_all_blocks()
            print(all_data)
            return all_data
        except Exception as e:
            print(f"Error in get_all_objects_by_type_id: {e}")
            self.conn.rollback()
            return TechCardData()
    
    def get_all_objects_by_type_id(self, type_id)->TechCardData:#получние все контролируемых элементов по id типа
        if not self.conn or not self.cursor:
            return TechCardData()
        try:
            self.cursor.execute('SELECT "blockId", name FROM blocks ORDER BY "blockId"')
            blocks_rows = self.cursor.fetchall()

            # Создаем словарь для результата
            blocks_dict = {}

            # Инициализируем словарь для каждого блока
            for block_row in blocks_rows:
                block_id = block_row["blockId"]
                block_name = block_row["name"]
                blocks_dict[block_id] = {
                    "name": block_name,
                    "params":{},
                }
            tech_card = TechCardData()
            tech_card.params = blocks_dict
            print(tech_card)
            return tech_card
        
        except Exception as e:
            print(f"Error in get_all_objects_by_type_id: {e}")
            self.conn.rollback()
            return TechCardData()
        

  
    def get_all_possible_values_by_param_and_element(self, element_type_id,param_id)->TechCardData:
        return TechCardData()

    def get_params_for_element(self, element_id: int) -> TechCardData:
        """Получить все параметры и их значения для конкретного элемента (objectControl) по его id."""
        return TechCardData()
    

    def get_all_blocks(self) -> List[Dict[str, Any]]:
        if not self.conn or not self.cursor:
            return TechCardData()
        try:
            self.cursor.execute('SELECT "blockId", name FROM blocks ORDER BY "blockId"')
            blocks_rows = self.cursor.fetchall()

            # Создаем словарь для результата
            blocks_dict = {}

            # Инициализируем словарь для каждого блока
            for block_row in blocks_rows:
                block_id = block_row["blockId"]
                block_name = block_row["name"]
                blocks_dict[block_id] = {
                    "name": block_name,
                    "params":{},
                }
            tech_card = TechCardData()
            tech_card.params = blocks_dict
            print(tech_card)
            return tech_card
        
        except Exception as e:
            print(f"Error in get_all_objects_by_type_id: {e}")
            self.conn.rollback()
            return TechCardData()
        

    def get_all_control_places(self) -> List[Dict[str, Any]]:
        """Получить все места контроля"""
        try:
            self.cursor.execute('SELECT id, name FROM control_places ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_control_places: {e}")
            return []

    def get_all_densitometer_types(self) -> List[Dict[str, Any]]:
        """Получить все типы денситометров"""
        try:
            self.cursor.execute('SELECT id, name FROM densitometer_types ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_densitometer_types: {e}")
            return []

    def get_all_development_times(self) -> List[Dict[str, Any]]:
        """Получить все времена проявления"""
        try:
            self.cursor.execute('SELECT id, name FROM development_times ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_development_times: {e}")
            return []

    def get_all_film_loading_types(self) -> List[Dict[str, Any]]:
        """Получить все типы загрузки пленки"""
        try:
            self.cursor.execute('SELECT id, name FROM film_loading_types ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_film_loading_types: {e}")
            return []

    def get_all_magnifier_types(self) -> List[Dict[str, Any]]:
        """Получить все типы луп"""
        try:
            self.cursor.execute('SELECT id, name FROM magnifier_types ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_magnifier_types: {e}")
            return []

    def get_all_manufacturers(self) -> List[Dict[str, Any]]:
        """Получить всех производителей"""
        try:
            self.cursor.execute('SELECT id, name, address FROM manufacturers ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_manufacturers: {e}")
            return []

    def get_all_marking_sections(self) -> List[Dict[str, Any]]:
        """Получить все участки маркировки"""
        try:
            self.cursor.execute('SELECT id, name FROM marking_sections ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_marking_sections: {e}")
            return []

    def get_all_marking_sign_types(self) -> List[Dict[str, Any]]:
        """Получить все типы знаков маркировки"""
        try:
            self.cursor.execute('SELECT id, name FROM marking_sign_types ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_marking_sign_types: {e}")
            return []

    def get_all_metals(self) -> List[Dict[str, Any]]:
        """Получить все типы металлов"""
        try:
            self.cursor.execute('SELECT id, name FROM metals ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_metals: {e}")
            return []

    def get_all_negatoscope_types(self) -> List[Dict[str, Any]]:
        """Получить все типы негатоскопов"""
        try:
            self.cursor.execute('SELECT id, name FROM negatoscope_types ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_negatoscope_types: {e}")
            return []

    def get_all_non_standard_cassettes(self) -> List[Dict[str, Any]]:
        """Получить все нестандартные кассеты"""
        try:
            self.cursor.execute('SELECT id, name FROM non_standard_cassettes ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_non_standard_cassettes: {e}")
            return []

    def get_all_paint_detector_types(self) -> List[Dict[str, Any]]:
        """Получить все типы дефектоскопических красок"""
        try:
            self.cursor.execute('SELECT id, name FROM paint_detector_types ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_paint_detector_types: {e}")
            return []

    def get_all_photo_processing_automatic(self) -> List[Dict[str, Any]]:
        """Получить все типы автоматической фотообработки"""
        try:
            self.cursor.execute('SELECT id, name FROM photo_processing_automatic ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_photo_processing_automatic: {e}")
            return []

    def get_all_protractor_types(self) -> List[Dict[str, Any]]:
        """Получить все типы угломеров"""
        try:
            self.cursor.execute('SELECT id, name FROM protractor_types ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_protractor_types: {e}")
            return []

    def get_all_radiation_sources(self) -> List[Dict[str, Any]]:
        """Получить все источники излучения"""
        try:
            self.cursor.execute('SELECT id, name, focal_spot_diameter FROM radiation_sources ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_radiation_sources: {e}")
            return []

    def get_all_radiographic_film_types(self) -> List[Dict[str, Any]]:
        """Получить все типы радиографической пленки"""
        try:
            self.cursor.execute('SELECT id, name FROM radiographic_film_types ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_radiographic_film_types: {e}")
            return []

    def get_all_ruler_types(self) -> List[Dict[str, Any]]:
        """Получить все типы линеек"""
        try:
            self.cursor.execute('SELECT id, name FROM ruler_types ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_ruler_types: {e}")
            return []

    def get_all_scope_of_controls(self) -> List[Dict[str, Any]]:
        """Получить все объемы контроля"""
        try:
            self.cursor.execute('SELECT id, name FROM scope_of_controls ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_scope_of_controls: {e}")
            return []

    def get_all_sensitivity_standard_types(self) -> List[Dict[str, Any]]:
        """Получить все типы эталонов чувствительности"""
        try:
            self.cursor.execute('SELECT id, name FROM sensitivity_standard_types ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_sensitivity_standard_types: {e}")
            return []

    def get_all_surface_quality_requirements(self) -> List[Dict[str, Any]]:
        """Получить все требования к качеству поверхности"""
        try:
            self.cursor.execute('SELECT id, name FROM surface_quality_requirements ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_surface_quality_requirements: {e}")
            return []

    def get_all_temperature_ranges(self) -> List[Dict[str, Any]]:
        """Получить все температурные диапазоны"""
        try:
            self.cursor.execute('SELECT id, name FROM temperature_ranges ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_temperature_ranges: {e}")
            return []

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Получить всех пользователей"""
        try:
            self.cursor.execute('SELECT id, name, username FROM users ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_users: {e}")
            return []

    def get_all_welded_joint_categories(self) -> List[Dict[str, Any]]:
        """Получить все категории сварных соединений"""
        try:
            self.cursor.execute('SELECT id, name FROM welded_joint_categories ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_welded_joint_categories: {e}")
            return []

    def get_all_welded_joint_types(self) -> List[Dict[str, Any]]:
        """Получить все типы сварных соединений"""
        try:
            self.cursor.execute('SELECT id, name FROM welded_joint_types ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_welded_joint_types: {e}")
            return []

    def get_all_welding_materials(self) -> List[Dict[str, Any]]:
        """Получить все сварочные материалы"""
        try:
            self.cursor.execute('SELECT id, name FROM welding_materials ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_welding_materials: {e}")
            return []

    def get_all_welding_methods(self) -> List[Dict[str, Any]]:
        """Получить все методы сварки"""
        try:
            self.cursor.execute('SELECT id, name FROM welding_methods ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_welding_methods: {e}")
            return []

    def get_all_working_link_compositions(self) -> List[Dict[str, Any]]:
        """Получить все составы рабочего звена"""
        try:
            self.cursor.execute('SELECT id, name FROM working_link_compositions ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_working_link_compositions: {e}")
            return []

    def get_all_drawing_numbers(self) -> List[Dict[str, Any]]:
        """Получить все номера чертежей"""
        try:
            self.cursor.execute("""
                SELECT dn.id, dn.name as drawing_number, m.name as manufacturer_name 
                FROM drawing_numbers dn
                LEFT JOIN manufacturers m ON dn.manufacturer_id = m.id
                ORDER BY dn.id
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_drawing_numbers: {e}")
            return []

    def get_all_detail_drawings(self) -> List[Dict[str, Any]]:
        """Получить все детальные чертежи"""
        try:
            self.cursor.execute("""
                SELECT dd.id, dd.name, dd.drawing_number_id, dn.name as drawing_number
                FROM detail_drawings dd
                LEFT JOIN drawing_numbers dn ON dd.drawing_number_id = dn.id
                ORDER BY dd.id
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_detail_drawings: {e}")
            return []

    def get_all_controlled_elements(self) -> List[Dict[str, Any]]:
        """Получить все контролируемые элементы"""
        try:
            self.cursor.execute("""
                SELECT ce.id, ce.name, ce.drawing_number_id, dn.name as drawing_number
                FROM controlled_elements ce
                LEFT JOIN drawing_numbers dn ON ce.drawing_number_id = dn.id
                ORDER BY ce.id
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_controlled_elements: {e}")
            return []

    def get_all_designations(self) -> List[Dict[str, Any]]:
        """Получить все обозначения"""
        try:
            self.cursor.execute("""
                SELECT d.id, d.name, d.drawing_number_id, dn.name as drawing_number, u.name as user_name
                FROM designations d
                LEFT JOIN drawing_numbers dn ON d.drawing_number_id = dn.id
                LEFT JOIN users u ON d.user_id = u.id
                ORDER BY d.id
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_designations: {e}")
            return []

    def get_all_transmission_schemes(self) -> List[Dict[str, Any]]:
        """Получить все схемы просвечивания"""
        try:
            self.cursor.execute("""
                SELECT ts.id, ts.reference, ts.welded_joint_type_id, wjt.name as welded_joint_type_name
                FROM transmission_schemes ts
                LEFT JOIN welded_joint_types wjt ON ts.welded_joint_type_id = wjt.id
                ORDER BY ts.id
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_transmission_schemes: {e}")
            return []

    def get_all_permissible_inclusion_standards(self) -> List[Dict[str, Any]]:
        """Получить все стандарты допустимых включений"""
        try:
            self.cursor.execute("""
                SELECT pis.id, pis.standard_code, pis.parameters, pis.detail_drawing_id, dd.name as detail_drawing_name
                FROM permissible_inclusion_standards pis
                LEFT JOIN detail_drawings dd ON pis.detail_drawing_id = dd.id
                ORDER BY pis.id
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_all_permissible_inclusion_standards: {e}")
            return []

    def get_all_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Получить все данные из всех таблиц одним вызовом
        """
        all_data = {}
        
        # Словарь методов для получения данных
        all_data=self.get_all_blocks() 
        print(all_data)
        
        # methods = {
        #     'blocks': self.get_all_blocks,
        #     'control_places': self.get_all_control_places,
        #     'densitometer_types': self.get_all_densitometer_types,
        #     'development_times': self.get_all_development_times,
        #     'film_loading_types': self.get_all_film_loading_types,
        #     'magnifier_types': self.get_all_magnifier_types,
        #     'manufacturers': self.get_all_manufacturers,
        #     'marking_sections': self.get_all_marking_sections,
        #     'marking_sign_types': self.get_all_marking_sign_types,
        #     'metals': self.get_all_metals,
        #     'negatoscope_types': self.get_all_negatoscope_types,
        #     'non_standard_cassettes': self.get_all_non_standard_cassettes,
        #     'paint_detector_types': self.get_all_paint_detector_types,
        #     'photo_processing_automatic': self.get_all_photo_processing_automatic,
        #     'protractor_types': self.get_all_protractor_types,
        #     'radiation_sources': self.get_all_radiation_sources,
        #     'radiographic_film_types': self.get_all_radiographic_film_types,
        #     'ruler_types': self.get_all_ruler_types,
        #     'scope_of_controls': self.get_all_scope_of_controls,
        #     'sensitivity_standard_types': self.get_all_sensitivity_standard_types,
        #     'surface_quality_requirements': self.get_all_surface_quality_requirements,
        #     'temperature_ranges': self.get_all_temperature_ranges,
        #     'users': self.get_all_users,
        #     'welded_joint_categories': self.get_all_welded_joint_categories,
        #     'welded_joint_types': self.get_all_welded_joint_types,
        #     'welding_materials': self.get_all_welding_materials,
        #     'welding_methods': self.get_all_welding_methods,
        #     'working_link_compositions': self.get_all_working_link_compositions,
        #     'drawing_numbers': self.get_all_drawing_numbers,
        #     'detail_drawings': self.get_all_detail_drawings,
        #     'controlled_elements': self.get_all_controlled_elements,
        #     'designations': self.get_all_designations,
        #     'transmission_schemes': self.get_all_transmission_schemes,
        #     'permissible_inclusion_standards': self.get_all_permissible_inclusion_standards
        # }
        
        # for key, method in methods.items():
        #     try:
        #         data = method()
        #         all_data[key] = data
        #         print(f"Загружено {len(data)} записей из таблицы {key}")
        #     except Exception as e:
        #         print(f"Ошибка при загрузке данных из {key}: {e}")
        #         all_data[key] = []
        
        return all_data

    def get_params_for_type(self, type_id):
        return self.get_all_blocks()

    def get_all_controlled_element_types(self) -> TechCardData:
        tech_card = TechCardData()
        tech_card.type = {1: "Контролируемый элемент"}
        return tech_card

    def get_all_objects_by_type_id(self, type_id) -> TechCardData:
        tech_card = self.get_all_blocks()
        elements = self.get_all_controlled_elements()
        element_dict = {
            row["id"]: row["name"]
            for row in elements
            if row.get("id") is not None and row.get("name")
        }

        if 1 not in tech_card.params:
            tech_card.params[1] = {
                "name": "Объект контроля",
                "params": {},
            }

        tech_card.params[1]["params"] = {
            "0": {
                "name": "Объект контроля",
                "val": element_dict or {1: "Техкарта Газпром"},
            }
        }
        return tech_card

    def get_params_for_element(self, element_id: int) -> TechCardData:
        element_row = self._fetch_one_row(
            """
            SELECT
                ce.id,
                ce.name AS controlled_element_name,
                dn.id AS drawing_number_id,
                dn.name AS drawing_number_name,
                m.name AS manufacturer_name,
                m.address AS manufacturer_address
            FROM controlled_elements ce
            LEFT JOIN drawing_numbers dn ON dn.id = ce.drawing_number_id
            LEFT JOIN manufacturers m ON m.id = dn.manufacturer_id
            WHERE ce.id = %s
            """,
            (element_id,),
        )

        if not element_row:
            return TechCardData()

        drawing_number_id = element_row.get("drawing_number_id")
        blocks: Dict[int, Dict[str, Any]] = {}

        object_block = self._append_block(blocks, "Объект контроля")
        self._add_param(object_block, "Контролируемый элемент", element_row.get("controlled_element_name"))
        self._add_param(object_block, "Номер чертежа", element_row.get("drawing_number_name"))
        self._add_param(object_block, "Изготовитель", element_row.get("manufacturer_name"))
        self._add_param(object_block, "Адрес изготовителя", element_row.get("manufacturer_address"))

        detail_drawings = self._fetch_all_rows(
            """
            SELECT id, name
            FROM detail_drawings
            WHERE drawing_number_id = %s
            ORDER BY id
            """,
            (drawing_number_id,),
        ) if drawing_number_id else []
        self._add_param(object_block, "Детальные чертежи", self._join_values(detail_drawings))

        designations = self._fetch_all_rows(
            """
            SELECT
                d.id,
                d.name,
                u.name AS user_name,
                u.username
            FROM designations d
            LEFT JOIN users u ON u.id = d.user_id
            WHERE d.drawing_number_id = %s
            ORDER BY d.id
            """,
            (drawing_number_id,),
        ) if drawing_number_id else []
        self._add_param(object_block, "Обозначения", self._join_values(designations))

        for designation in designations:
            designation_id = designation["id"]
            designation_name = designation.get("name") or f'Обозначение {designation_id}'

            designation_block = self._append_block(blocks, f"Параметры обозначения: {designation_name}")
            self._add_param(designation_block, "Обозначение", designation_name)
            self._add_param(designation_block, "Пользователь", designation.get("user_name"))
            self._add_param(designation_block, "Логин пользователя", designation.get("username"))

            designation_params_rows = self._fetch_all_rows(
                """
                SELECT
                    dp.id,
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
                """,
                (designation_id,),
            )
            for row in designation_params_rows:
                self._add_param(designation_block, "Тип сварного соединения", row.get("welded_joint_type_name"))
                self._add_param(designation_block, "Метод сварки", row.get("welding_method_name"))
                self._add_param(designation_block, "Металл", row.get("metal_name"))
                self._add_param(designation_block, "Сварочный материал", row.get("welding_material_name"))
                self._add_param(designation_block, "Категория сварного соединения", row.get("welded_joint_category_name"))
                self._add_param(designation_block, "Объем контроля", row.get("scope_of_control_name"))
                self._add_param(designation_block, "Источник излучения", row.get("radiation_source_name"))
                self._add_param(designation_block, "Размер фокусного пятна", row.get("focal_spot_diameter"))
                self._add_param(designation_block, "Тип эталона чувствительности", row.get("sensitivity_standard_type_name"))
                self._add_param(designation_block, "Тип знака маркировки", row.get("marking_sign_type_name"))
                self._add_param(designation_block, "Нестандартная кассета", row.get("non_standard_cassette_name"))
                self._add_param(designation_block, "Тип лупы", row.get("magnifier_type_name"))
                self._add_param(designation_block, "Тип денситометра", row.get("densitometer_type_name"))
                self._add_param(designation_block, "Тип негатоскопа", row.get("negatoscope_type_name"))
                self._add_param(designation_block, "Тип линейки", row.get("ruler_type_name"))
                self._add_param(designation_block, "Тип угломера", row.get("protractor_type_name"))
                self._add_param(designation_block, "Тип дефектоскопической краски", row.get("paint_detector_type_name"))

            dimensions_block = self._append_block(blocks, f"Размеры: {designation_name}")
            dimensions_rows = self._fetch_all_rows(
                """
                SELECT id, text, value
                FROM dimensions
                WHERE designation_id = %s
                ORDER BY id
                """,
                (designation_id,),
            )
            for row in dimensions_rows:
                self._add_param(
                    dimensions_block,
                    row.get("text") or f'Размер {row["id"]}',
                    row.get("value"),
                )

            preparation_block = self._append_block(blocks, f"Подготовка элемента: {designation_name}")
            preparation_rows = self._fetch_all_rows(
                """
                SELECT
                    ep.id,
                    sqr.name AS surface_quality_requirement_name,
                    ms.name AS marking_section_name
                FROM element_preparation ep
                LEFT JOIN surface_quality_requirements sqr ON sqr.id = ep.surface_quality_requirement_id
                LEFT JOIN marking_sections ms ON ms.id = ep.marking_section_id
                WHERE ep.designation_id = %s
                ORDER BY ep.id
                """,
                (designation_id,),
            )
            for index, row in enumerate(preparation_rows, start=1):
                suffix = f" #{index}" if len(preparation_rows) > 1 else ""
                self._add_param(preparation_block, f"Требование к качеству поверхности{suffix}", row.get("surface_quality_requirement_name"))
                self._add_param(preparation_block, f"Участок маркировки{suffix}", row.get("marking_section_name"))

            control_terms_block = self._append_block(blocks, f"Условия контроля: {designation_name}")
            control_terms_rows = self._fetch_all_rows(
                """
                SELECT
                    ct.id,
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
                """,
                (designation_id,),
            )
            for index, row in enumerate(control_terms_rows, start=1):
                suffix = f" #{index}" if len(control_terms_rows) > 1 else ""
                self._add_param(control_terms_block, f"Место контроля{suffix}", row.get("control_place_name"))
                self._add_param(control_terms_block, f"Состав рабочего звена{suffix}", row.get("working_link_composition_name"))
                self._add_param(control_terms_block, f"Температурный диапазон{suffix}", row.get("temperature_range_name"))
                self._add_param(control_terms_block, f"Автоматическая фотообработка{suffix}", row.get("photo_processing_automatic_name"))
                self._add_param(control_terms_block, f"Время проявления{suffix}", row.get("development_time_name"))

            film_block = self._append_block(blocks, f"Пленка: {designation_name}")
            film_loading_rows = self._fetch_all_rows(
                """
                SELECT
                    flu.id,
                    flt.name AS film_loading_type_name
                FROM film_loading_usage flu
                LEFT JOIN film_loading_types flt ON flt.id = flu.film_loading_type_id
                WHERE flu.designation_id = %s
                ORDER BY flu.id
                """,
                (designation_id,),
            )
            for index, row in enumerate(film_loading_rows, start=1):
                suffix = f" #{index}" if len(film_loading_rows) > 1 else ""
                self._add_param(film_block, f"Тип загрузки пленки{suffix}", row.get("film_loading_type_name"))

            film_usage_rows = self._fetch_all_rows(
                """
                SELECT
                    fu.id,
                    rft.name AS radiographic_film_type_name
                FROM film_usage fu
                LEFT JOIN radiographic_film_types rft ON rft.id = fu.radiographic_film_type_id
                WHERE fu.designation_id = %s
                ORDER BY fu.id
                """,
                (designation_id,),
            )
            for index, row in enumerate(film_usage_rows, start=1):
                suffix = f" #{index}" if len(film_usage_rows) > 1 else ""
                self._add_param(film_block, f"Тип радиографической пленки{suffix}", row.get("radiographic_film_type_name"))

            decoding_block = self._append_block(blocks, f"Расшифровка радиографии: {designation_name}")
            decoding_rows = self._fetch_all_rows(
                """
                SELECT id, parameters
                FROM radiographic_decoding_types
                WHERE designation_id = %s
                ORDER BY id
                """,
                (designation_id,),
            )
            for index, row in enumerate(decoding_rows, start=1):
                self._add_param(decoding_block, f"Параметры расшифровки #{index}", row.get("parameters"))

            quality_block = self._append_block(blocks, f"Оценка качества: {designation_name}")
            quality_rows = self._fetch_all_rows(
                """
                SELECT id, parameters
                FROM quality_assessment_types
                WHERE designation_id = %s
                ORDER BY id
                """,
                (designation_id,),
            )
            for index, row in enumerate(quality_rows, start=1):
                self._add_param(quality_block, f"Параметры оценки #{index}", row.get("parameters"))

            operations_block = self._append_block(blocks, f"Технологические операции: {designation_name}")
            operation_rows = self._fetch_all_rows(
                """
                SELECT
                    tos.id,
                    tos.control_term_id,
                    tos.operation_index,
                    tos.operation_name
                FROM tech_operation_sequences tos
                INNER JOIN control_terms ct ON ct.id = tos.control_term_id
                WHERE ct.designation_id = %s
                ORDER BY ct.id, tos.operation_index, tos.id
                """,
                (designation_id,),
            )
            for row in operation_rows:
                operation_index = row.get("operation_index") or row.get("id")
                self._add_param(operations_block, f"Операция {operation_index}", row.get("operation_name"))

        permissible_block = self._append_block(blocks, "Допустимые включения")
        permissible_rows = self._fetch_all_rows(
            """
            SELECT
                pis.id,
                dd.name AS detail_drawing_name,
                pis.standard_code,
                pis.parameters
            FROM permissible_inclusion_standards pis
            LEFT JOIN detail_drawings dd ON dd.id = pis.detail_drawing_id
            WHERE dd.drawing_number_id = %s
            ORDER BY pis.id
            """,
            (drawing_number_id,),
        ) if drawing_number_id else []
        for index, row in enumerate(permissible_rows, start=1):
            drawing_name = row.get("detail_drawing_name") or f"Чертеж {index}"
            self._add_param(permissible_block, f"{drawing_name}: код стандарта", row.get("standard_code"))
            self._add_param(permissible_block, f"{drawing_name}: параметры", row.get("parameters"))

        tech_card = TechCardData(typeObjectControl="Контролируемый элемент")
        tech_card.params = blocks
        return tech_card

    def _fetch_all_rows(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        if not self.conn or not self.cursor:
            return []
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in query execution: {e}")
            self.conn.rollback()
            return []

    def _fetch_one_row(self, query: str, params: tuple = ()) -> Dict[str, Any] | None:
        if not self.conn or not self.cursor:
            return None
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error in query execution: {e}")
            self.conn.rollback()
            return None

    def _create_block(self, name: str) -> Dict[str, Any]:
        return {
            "name": name,
            "params": {},
        }

    def _append_block(self, blocks: Dict[int, Dict[str, Any]], name: str) -> Dict[str, Any]:
        block_id = max(blocks.keys(), default=0) + 1
        blocks[block_id] = self._create_block(name)
        return blocks[block_id]

    def _add_param(self, block: Dict[str, Any], name: str, value: Any, param_id: Any = None) -> None:
        if value is None:
            return
        if isinstance(value, str) and value == "":
            return
        if isinstance(value, list) and len(value) == 0:
            return

        params = block.setdefault("params", {})
        if param_id is None:
            next_id = 1
            while next_id in params:
                next_id += 1
            param_id = next_id

        params[param_id] = {
            "name": name,
            "val": value,
        }

    def _rows_to_names(self, rows: List[Dict[str, Any]], key: str = "name") -> List[str]:
        values = []
        for row in rows:
            value = row.get(key)
            if value:
                values.append(str(value))
        return values

    def _join_values(self, rows: List[Dict[str, Any]], key: str = "name") -> str | None:
        values = self._rows_to_names(rows, key)
        if not values:
            return None
        return "; ".join(values)

    def _build_gazprom_template_blocks(self) -> Dict[int, Dict[str, Any]]:
        blocks: Dict[int, Dict[str, Any]] = {}

        object_block = self._append_block(blocks, "Объект контроля")
        controlled_elements = self.get_all_controlled_elements()
        drawing_numbers = self.get_all_drawing_numbers()
        self._add_param(
            object_block,
            "Контролируемый элемент",
            [row["name"] for row in controlled_elements if row.get("name")],
        )
        self._add_param(
            object_block,
            "Номер чертежа",
            [row["drawing_number"] for row in drawing_numbers if row.get("drawing_number")],
        )

        designation_block = self._append_block(blocks, "Параметры обозначения")
        designation_references = [
            ("Тип сварного соединения", self.get_all_welded_joint_types()),
            ("Метод сварки", self.get_all_welding_methods()),
            ("Металл", self.get_all_metals()),
            ("Сварочный материал", self.get_all_welding_materials()),
            ("Категория сварного соединения", self.get_all_welded_joint_categories()),
            ("Объем контроля", self.get_all_scope_of_controls()),
            ("Источник излучения", self.get_all_radiation_sources()),
            ("Тип эталона чувствительности", self.get_all_sensitivity_standard_types()),
            ("Тип маркировочного знака", self.get_all_marking_sign_types()),
            ("Нестандартная кассета", self.get_all_non_standard_cassettes()),
            ("Тип лупы", self.get_all_magnifier_types()),
            ("Тип денситометра", self.get_all_densitometer_types()),
            ("Тип негатоскопа", self.get_all_negatoscope_types()),
            ("Тип линейки", self.get_all_ruler_types()),
            ("Тип угломера", self.get_all_protractor_types()),
            ("Тип дефектоскопической краски", self.get_all_paint_detector_types()),
        ]
        for name, rows in designation_references:
            self._add_param(designation_block, name, self._rows_to_names(rows))

        preparation_block = self._append_block(blocks, "Подготовка элемента")
        self._add_param(preparation_block, "Требование к качеству поверхности", self._rows_to_names(self.get_all_surface_quality_requirements()))
        self._add_param(preparation_block, "Участок маркировки", self._rows_to_names(self.get_all_marking_sections()))

        control_terms_block = self._append_block(blocks, "Условия контроля")
        self._add_param(control_terms_block, "Место контроля", self._rows_to_names(self.get_all_control_places()))
        self._add_param(control_terms_block, "Состав рабочего звена", self._rows_to_names(self.get_all_working_link_compositions()))
        self._add_param(control_terms_block, "Температурный диапазон", self._rows_to_names(self.get_all_temperature_ranges()))
        self._add_param(control_terms_block, "Автоматическая фотообработка", self._rows_to_names(self.get_all_photo_processing_automatic()))
        self._add_param(control_terms_block, "Время проявления", self._rows_to_names(self.get_all_development_times()))

        film_block = self._append_block(blocks, "Пленка")
        self._add_param(film_block, "Тип загрузки пленки", self._rows_to_names(self.get_all_film_loading_types()))
        self._add_param(film_block, "Тип радиографической пленки", self._rows_to_names(self.get_all_radiographic_film_types()))

        scheme_block = self._append_block(blocks, "Схемы и нормы")
        self._add_param(scheme_block, "Схемы просвечивания", self._rows_to_names(self.get_all_transmission_schemes(), "reference"))
        self._add_param(scheme_block, "Стандарты допустимых включений", self._rows_to_names(self.get_all_permissible_inclusion_standards(), "standard_code"))

        return blocks

    def get_params_for_type(self, type_id):
        tech_card = TechCardData(typeObjectControl="Контролируемый элемент")
        tech_card.params = self._build_gazprom_template_blocks()
        return tech_card

    def get_all_controlled_element_types(self) -> TechCardData:
        tech_card = TechCardData()
        tech_card.type = {1: "Контролируемый элемент"}
        return tech_card

    def get_all_objects_by_type_id(self, type_id) -> TechCardData:
        elements = self._fetch_all_rows(
            """
            SELECT
                ce.id,
                ce.name,
                dn.name AS drawing_number
            FROM controlled_elements ce
            LEFT JOIN drawing_numbers dn ON dn.id = ce.drawing_number_id
            ORDER BY ce.name, ce.id
            """
        )

        element_dict = {}
        for row in elements:
            if row.get("id") is None or not row.get("name"):
                continue
            display_name = row["name"]
            if row.get("drawing_number"):
                display_name = f'{display_name} ({row["drawing_number"]})'
            element_dict[row["id"]] = display_name

        tech_card = TechCardData()
        tech_card.params = {
            1: {
                "name": "Объект контроля",
                "params": {
                    "0": {
                        "name": "Объект контроля",
                        "val": element_dict,
                    }
                },
            }
        }
        return tech_card

    def get_all_possible_values_by_param_and_element(self, element_type_id, param_id) -> TechCardData:
        template = self.get_params_for_type(element_type_id)
        for block in template.params.values():
            params = block.get("params", {})
            param = params.get(param_id) or params.get(str(param_id))
            if not param:
                continue

            value = param.get("val")
            if isinstance(value, list):
                tech_card = TechCardData()
                tech_card.params = {param_id: value}
                return tech_card

        return TechCardData()

    def get_params_for_element(self, element_id: int) -> TechCardData:
        element_row = self._fetch_one_row(
            """
            SELECT
                ce.id,
                ce.name AS controlled_element_name,
                dn.id AS drawing_number_id,
                dn.name AS drawing_number_name,
                m.name AS manufacturer_name,
                m.address AS manufacturer_address
            FROM controlled_elements ce
            LEFT JOIN drawing_numbers dn ON dn.id = ce.drawing_number_id
            LEFT JOIN manufacturers m ON m.id = dn.manufacturer_id
            WHERE ce.id = %s
            """,
            (element_id,),
        )

        if not element_row:
            return TechCardData()

        drawing_number_id = element_row.get("drawing_number_id")
        blocks: Dict[int, Dict[str, Any]] = {}

        object_block = self._append_block(blocks, "Объект контроля")
        self._add_param(object_block, "Контролируемый элемент", element_row.get("controlled_element_name"))
        self._add_param(object_block, "Номер чертежа", element_row.get("drawing_number_name"))
        self._add_param(object_block, "Изготовитель", element_row.get("manufacturer_name"))
        self._add_param(object_block, "Адрес изготовителя", element_row.get("manufacturer_address"))

        detail_drawings = self._fetch_all_rows(
            """
            SELECT id, name
            FROM detail_drawings
            WHERE drawing_number_id = %s
            ORDER BY id
            """,
            (drawing_number_id,),
        ) if drawing_number_id else []
        self._add_param(object_block, "Детальные чертежи", self._join_values(detail_drawings))

        designations = self._fetch_all_rows(
            """
            SELECT
                d.id,
                d.name,
                u.name AS user_name,
                u.username
            FROM designations d
            LEFT JOIN users u ON u.id = d.user_id
            WHERE d.drawing_number_id = %s
            ORDER BY d.id
            """,
            (drawing_number_id,),
        ) if drawing_number_id else []
        self._add_param(object_block, "Обозначения", self._join_values(designations))

        for designation in designations:
            designation_id = designation["id"]
            designation_name = designation.get("name") or f'Обозначение {designation_id}'

            designation_block = self._append_block(blocks, f"Параметры обозначения: {designation_name}")
            self._add_param(designation_block, "Обозначение", designation_name)
            self._add_param(designation_block, "Пользователь", designation.get("user_name"))
            self._add_param(designation_block, "Логин пользователя", designation.get("username"))

            designation_params_rows = self._fetch_all_rows(
                """
                SELECT
                    dp.id,
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
                """,
                (designation_id,),
            )
            for row in designation_params_rows:
                self._add_param(designation_block, "Тип сварного соединения", row.get("welded_joint_type_name"))
                self._add_param(designation_block, "Метод сварки", row.get("welding_method_name"))
                self._add_param(designation_block, "Металл", row.get("metal_name"))
                self._add_param(designation_block, "Сварочный материал", row.get("welding_material_name"))
                self._add_param(designation_block, "Категория сварного соединения", row.get("welded_joint_category_name"))
                self._add_param(designation_block, "Объем контроля", row.get("scope_of_control_name"))
                self._add_param(designation_block, "Источник излучения", row.get("radiation_source_name"))
                self._add_param(designation_block, "Размер фокусного пятна", row.get("focal_spot_diameter"))
                self._add_param(designation_block, "Тип эталона чувствительности", row.get("sensitivity_standard_type_name"))
                self._add_param(designation_block, "Тип знака маркировки", row.get("marking_sign_type_name"))
                self._add_param(designation_block, "Нестандартная кассета", row.get("non_standard_cassette_name"))
                self._add_param(designation_block, "Тип лупы", row.get("magnifier_type_name"))
                self._add_param(designation_block, "Тип денситометра", row.get("densitometer_type_name"))
                self._add_param(designation_block, "Тип негатоскопа", row.get("negatoscope_type_name"))
                self._add_param(designation_block, "Тип линейки", row.get("ruler_type_name"))
                self._add_param(designation_block, "Тип угломера", row.get("protractor_type_name"))
                self._add_param(designation_block, "Тип дефектоскопической краски", row.get("paint_detector_type_name"))

            dimensions_block = self._append_block(blocks, f"Размеры: {designation_name}")
            dimensions_rows = self._fetch_all_rows(
                """
                SELECT id, text, value
                FROM dimensions
                WHERE designation_id = %s
                ORDER BY id
                """,
                (designation_id,),
            )
            for row in dimensions_rows:
                self._add_param(
                    dimensions_block,
                    row.get("text") or f'Размер {row["id"]}',
                    row.get("value"),
                )

            preparation_block = self._append_block(blocks, f"Подготовка элемента: {designation_name}")
            preparation_rows = self._fetch_all_rows(
                """
                SELECT
                    ep.id,
                    sqr.name AS surface_quality_requirement_name,
                    ms.name AS marking_section_name
                FROM element_preparation ep
                LEFT JOIN surface_quality_requirements sqr ON sqr.id = ep.surface_quality_requirement_id
                LEFT JOIN marking_sections ms ON ms.id = ep.marking_section_id
                WHERE ep.designation_id = %s
                ORDER BY ep.id
                """,
                (designation_id,),
            )
            for index, row in enumerate(preparation_rows, start=1):
                suffix = f" #{index}" if len(preparation_rows) > 1 else ""
                self._add_param(preparation_block, f"Требование к качеству поверхности{suffix}", row.get("surface_quality_requirement_name"))
                self._add_param(preparation_block, f"Участок маркировки{suffix}", row.get("marking_section_name"))

            control_terms_block = self._append_block(blocks, f"Условия контроля: {designation_name}")
            control_terms_rows = self._fetch_all_rows(
                """
                SELECT
                    ct.id,
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
                """,
                (designation_id,),
            )
            for index, row in enumerate(control_terms_rows, start=1):
                suffix = f" #{index}" if len(control_terms_rows) > 1 else ""
                self._add_param(control_terms_block, f"Место контроля{suffix}", row.get("control_place_name"))
                self._add_param(control_terms_block, f"Состав рабочего звена{suffix}", row.get("working_link_composition_name"))
                self._add_param(control_terms_block, f"Температурный диапазон{suffix}", row.get("temperature_range_name"))
                self._add_param(control_terms_block, f"Автоматическая фотообработка{suffix}", row.get("photo_processing_automatic_name"))
                self._add_param(control_terms_block, f"Время проявления{suffix}", row.get("development_time_name"))

            film_block = self._append_block(blocks, f"Пленка: {designation_name}")
            film_loading_rows = self._fetch_all_rows(
                """
                SELECT
                    flu.id,
                    flt.name AS film_loading_type_name
                FROM film_loading_usage flu
                LEFT JOIN film_loading_types flt ON flt.id = flu.film_loading_type_id
                WHERE flu.designation_id = %s
                ORDER BY flu.id
                """,
                (designation_id,),
            )
            for index, row in enumerate(film_loading_rows, start=1):
                suffix = f" #{index}" if len(film_loading_rows) > 1 else ""
                self._add_param(film_block, f"Тип загрузки пленки{suffix}", row.get("film_loading_type_name"))

            film_usage_rows = self._fetch_all_rows(
                """
                SELECT
                    fu.id,
                    rft.name AS radiographic_film_type_name
                FROM film_usage fu
                LEFT JOIN radiographic_film_types rft ON rft.id = fu.radiographic_film_type_id
                WHERE fu.designation_id = %s
                ORDER BY fu.id
                """,
                (designation_id,),
            )
            for index, row in enumerate(film_usage_rows, start=1):
                suffix = f" #{index}" if len(film_usage_rows) > 1 else ""
                self._add_param(film_block, f"Тип радиографической пленки{suffix}", row.get("radiographic_film_type_name"))

            decoding_block = self._append_block(blocks, f"Расшифровка радиографии: {designation_name}")
            decoding_rows = self._fetch_all_rows(
                """
                SELECT id, parameters
                FROM radiographic_decoding_types
                WHERE designation_id = %s
                ORDER BY id
                """,
                (designation_id,),
            )
            for index, row in enumerate(decoding_rows, start=1):
                self._add_param(decoding_block, f"Параметры расшифровки #{index}", row.get("parameters"))

            quality_block = self._append_block(blocks, f"Оценка качества: {designation_name}")
            quality_rows = self._fetch_all_rows(
                """
                SELECT id, parameters
                FROM quality_assessment_types
                WHERE designation_id = %s
                ORDER BY id
                """,
                (designation_id,),
            )
            for index, row in enumerate(quality_rows, start=1):
                self._add_param(quality_block, f"Параметры оценки #{index}", row.get("parameters"))

            operations_block = self._append_block(blocks, f"Технологические операции: {designation_name}")
            operation_rows = self._fetch_all_rows(
                """
                SELECT
                    tos.id,
                    tos.control_term_id,
                    tos.operation_index,
                    tos.operation_name
                FROM tech_operation_sequences tos
                INNER JOIN control_terms ct ON ct.id = tos.control_term_id
                WHERE ct.designation_id = %s
                ORDER BY ct.id, tos.operation_index, tos.id
                """,
                (designation_id,),
            )
            for row in operation_rows:
                operation_index = row.get("operation_index") or row.get("id")
                self._add_param(operations_block, f"Операция {operation_index}", row.get("operation_name"))

        permissible_block = self._append_block(blocks, "Допустимые включения")
        permissible_rows = self._fetch_all_rows(
            """
            SELECT
                pis.id,
                dd.name AS detail_drawing_name,
                pis.standard_code,
                pis.parameters
            FROM permissible_inclusion_standards pis
            LEFT JOIN detail_drawings dd ON dd.id = pis.detail_drawing_id
            WHERE dd.drawing_number_id = %s
            ORDER BY pis.id
            """,
            (drawing_number_id,),
        ) if drawing_number_id else []
        for index, row in enumerate(permissible_rows, start=1):
            drawing_name = row.get("detail_drawing_name") or f"Чертеж {index}"
            self._add_param(permissible_block, f"{drawing_name}: код стандарта", row.get("standard_code"))
            self._add_param(permissible_block, f"{drawing_name}: параметры", row.get("parameters"))

        tech_card = TechCardData(typeObjectControl="Контролируемый элемент")
        tech_card.params = blocks
        return tech_card

    def get_params_for_element(self, element_id: int) -> TechCardData:
        tech_card = self.get_all_blocks()
        tech_card.type = "Контролируемый элемент"

        if 1 not in tech_card.params:
            tech_card.params[1] = {
                "name": "Объект контроля",
                "params": {},
            }

        selected_element = next(
            (row for row in self.get_all_controlled_elements() if row.get("id") == element_id),
            None,
        )
        tech_card.params[1]["params"]["0"] = {
            "name": "Объект контроля",
            "val": {
                "id": element_id,
                "name": selected_element.get("name") if selected_element else "Техкарта Газпром",
            }
        }
        return tech_card
