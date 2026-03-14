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