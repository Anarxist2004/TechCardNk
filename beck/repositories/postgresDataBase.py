from interfaces.i_repository import IRepository
from services.tech_card import TechCardData
from services.tech_card import TypeObjectControl
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor


class PostgresDataBase(IRepository[TechCardData]):
    """
    Репозиторий для работы с БД в соответствии со схемой:
    - blocks (blockId, name)
    - material (idMaterial, name)
    - objectControl (id, idTypeControl, name)
    - paramsDefinition (id, name, typeData, idBlock)
    - paramsObjectControl (idObjectControl, idDefParams, valueInt, valueDouble, valueString, valueBool, id, imageRef)
    - typeOfControlledElement (Id, name)
    - typeParams (id, idTypeDefParam, idTypeControlEl, dafauilValue)
    """

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

    def findParamsByCurentParam(self, data: TechCardData) -> TechCardData:
        """
        Поиск доступных параметров по текущим выбранным параметрам.
        Использует таблицы: objectControl, typeOfControlledElement, paramsDefinition, paramsObjectControl.
        """
        if not self.conn or not self.cursor:
            return data
        try:
            current_params = data.params
            query_conditions = []
            query_params: List[object] = []

            type_control_id = current_params.get("typeOfControlledElement")
            if type_control_id is not None:
                query_conditions.append('oc."idTypeControl" = %s')
                query_params.append(type_control_id)

            if current_params:
                param_subqueries = []
                for param_name, param_value in current_params.items():
                    if param_name == "typeOfControlledElement":
                        continue
                    self.cursor.execute(
                        'SELECT id FROM "paramsDefinition" WHERE name = %s',
                        (param_name,),
                    )
                    param_def_result = self.cursor.fetchone()
                    if param_def_result:
                        param_def_id = param_def_result["id"]
                        param_subqueries.append("""
                            EXISTS (
                                SELECT 1 FROM "paramsObjectControl" poc
                                WHERE poc."idObjectControl" = oc.id
                                AND poc."idDefParams" = %s
                                AND (
                                    (poc."valueInt" = %s)
                                    OR (poc."valueDouble" = %s)
                                    OR (poc."valueString" = %s)
                                    OR (poc."valueBool" = %s)
                                )
                            )
                        """)
                        query_params.extend([
                            param_def_id,
                            param_value if isinstance(param_value, int) else None,
                            param_value if isinstance(param_value, float) else None,
                            param_value if isinstance(param_value, str) else None,
                            param_value if isinstance(param_value, bool) else None,
                        ])
                if param_subqueries:
                    query_conditions.append("(" + " AND ".join(param_subqueries) + ")")

            query = """
                SELECT oc.id, oc.name, oc."idTypeControl", tce.name AS type_name
                FROM "objectControl" oc
                JOIN "typeOfControlledElement" tce ON oc."idTypeControl" = tce."Id"
            """
            if query_conditions:
                query += " WHERE " + " AND ".join(query_conditions)

            self.cursor.execute(query, query_params)
            matching_objects = self.cursor.fetchall()

            if not matching_objects:
                return data

            object_ids = [obj["id"] for obj in matching_objects]

            self.cursor.execute("""
                SELECT
                    pd.name AS param_name,
                    pd."typeData",
                    poc."valueInt",
                    poc."valueDouble",
                    poc."valueString",
                    poc."valueBool",
                    oc."idTypeControl"
                FROM "paramsObjectControl" poc
                JOIN "paramsDefinition" pd ON poc."idDefParams" = pd.id
                JOIN "objectControl" oc ON poc."idObjectControl" = oc.id
                WHERE poc."idObjectControl" = ANY(%s)
                ORDER BY pd.name
            """, (object_ids,))

            all_params = self.cursor.fetchall()
            param_values: dict = {}
            for row in all_params:
                param_name = row["param_name"]
                type_data = row["typeData"]
                obj_type_id = row["idTypeControl"]
                if type_control_id is not None and obj_type_id != type_control_id:
                    continue
                v_int = row["valueInt"]
                v_double = row["valueDouble"]
                v_string = row["valueString"]
                v_bool = row["valueBool"]
                if type_data and type_data.lower() == "int" and v_int is not None:
                    value = v_int
                elif type_data and type_data.lower() == "double" and v_double is not None:
                    value = v_double
                elif type_data and type_data.lower() == "string" and v_string is not None:
                    value = v_string
                elif type_data and type_data.lower() == "bool" and v_bool is not None:
                    value = v_bool
                else:
                    continue
                if param_name not in param_values:
                    param_values[param_name] = set()
                param_values[param_name].add(value)

            self.cursor.execute(
                'SELECT "Id", name FROM "typeOfControlledElement" ORDER BY "Id"'
            )
            type_options = self.cursor.fetchall()

            for param_name, values_set in param_values.items():
                data.set_params(param_name, sorted(list(values_set)))
            if type_options:
                type_list = [{"id": t["Id"], "name": t["name"]} for t in type_options]
                data.set_params("typeOfControlledElement", type_list)

            return data
        except Exception as e:
            print(f"Error in findParamsByCurentParam: {e}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            raise

    _NO_BLOCK_NAME = "Без блока"

    def getParamDefinitions(self) -> List[dict]:
        """
        Список блоков с параметрами. Каждый блок: { "blockId", "name", "params": [ {id, name, type} ] }.
        Пустые блоки включаются. Параметры с idBlock IS NULL в блоке «Без блока».
        """
        if not self.conn or not self.cursor:
            return []
        try:
            self.cursor.execute('SELECT "blockId", name FROM blocks ORDER BY "blockId"')
            blocks_rows = self.cursor.fetchall()
            self.cursor.execute("""
                SELECT id, name, "typeData", "idBlock"
                FROM "paramsDefinition"
                ORDER BY "idBlock" NULLS LAST, name
            """)
            params_rows = self.cursor.fetchall()
            result = []
            for block in blocks_rows:
                block_id, block_name = block["blockId"], block["name"]
                params_in_block = [
                    {"id": r["id"], "name": r["name"], "type": r["typeData"]}
                    for r in params_rows
                    if r["idBlock"] == block_id
                ]
                result.append({"blockId": block_id, "name": block_name, "params": params_in_block})
            no_block_params = [
                {"id": r["id"], "name": r["name"], "type": r["typeData"]}
                for r in params_rows
                if r["idBlock"] is None
            ]
            if no_block_params:
                result.append({"blockId": None, "name": self._NO_BLOCK_NAME, "params": no_block_params})
            return result
        except Exception as e:
            print(f"Error in getParamDefinitions: {e}")
            self.conn.rollback()
            return []

    def get_params_for_type(self, type_id: int) -> TechCardData:
        """
        Параметры для типа, сгруппированные по блокам.
        Формат:
        {
            block_id: {
                "name": block_name,
                "params": {
                    param_id: {
                        "name": param_name,
                        "val": None  # или можно указать тип данных
                    }
                }
            }
        }
        """
        if not self.conn or not self.cursor:
            return TechCardData()
        try:
            # Получаем все блоки
            self.cursor.execute('SELECT "blockId", name FROM blocks ORDER BY "blockId"')
            blocks_rows = self.cursor.fetchall()

            # Инициализируем словарь для результата в нужном формате
            blocks_dict = {}
            for block_row in blocks_rows:
                block_id = block_row["blockId"]
                block_name = block_row["name"]
                blocks_dict[block_id] = {
                    "name": block_name,
                    "params": {}
                }

            # Получаем параметры для типа
            self.cursor.execute("""
                SELECT 
                    pd.id AS param_id,
                    pd.name AS param_name,
                    pd."typeData",
                    pd."idBlock",
                    b."blockId",
                    b.name AS block_name
                FROM "paramsDefinition" pd
                INNER JOIN "typeParams" tp ON pd.id = tp."idTypeDefParam"
                LEFT JOIN blocks b ON pd."idBlock" = b."blockId"
                WHERE tp."idTypeControlEl" = %s
                ORDER BY b."blockId" NULLS LAST, pd.name
            """, (type_id,))
            rows = self.cursor.fetchall()

            # Собираем все параметры для каждого блока
            for row in rows:
                block_id = row["blockId"] if row["blockId"] is not None else 1
                if block_id not in blocks_dict:
                    # Если блока нет в словаре, добавляем его
                    block_name = row["block_name"] if row["block_name"] else "Без блока"
                    blocks_dict[block_id] = {
                        "name": block_name,
                        "params": {}
                    }
                
                # Добавляем параметр в структуру
                param_id = row["param_id"]
                param_name = row["param_name"]
                if param_name is not None:
                    blocks_dict[block_id]["params"][param_id] = {
                        "name": param_name,
                        "val": None  # Для типа показываем только названия параметров
                    }

            tech_card = TechCardData()
            tech_card.params = blocks_dict
            return tech_card
        except Exception as e:
            print(f"Error in get_params_for_type: {e}")
            self.conn.rollback()
            return TechCardData()

    def get_all_controlled_element_types(self) -> TechCardData:
        """Все типы контролируемых элементов из typeOfControlledElement."""
        if not self.conn or not self.cursor:
            return TechCardData()
        try:
            self.cursor.execute("""
                SELECT "Id" AS id, name
                FROM "typeOfControlledElement"
                ORDER BY name
            """)
            rows = self.cursor.fetchall()
            id_name_dict = {row["id"]: row["name"] for row in rows}
            tech_card = TechCardData()
            tech_card.type = id_name_dict
            print(id_name_dict)
            return tech_card
        except Exception as e:
            print(f"Error in get_all_controlled_element_types: {e}")
            self.conn.rollback()
            return TechCardData()

    def get_all_objects_by_type_id(self, type_id: int) -> TechCardData:
        """Объекты контроля по ID типа из objectControl."""
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


            self.cursor.execute("""
                SELECT id, name
                FROM "objectControl"
                WHERE "idTypeControl" = %s
                ORDER BY name
            """, (type_id,))
            rows = self.cursor.fetchall()
            id_name_dict = {row["id"]: row["name"] for row in rows}

            blocks_dict[1]['params']={"0":{"name":'Объект контроля','val':{}}}
            blocks_dict[1]['params']['0']['val'] = id_name_dict

            tech_card = TechCardData()
            tech_card.params = blocks_dict
            return tech_card
        except Exception as e:
            print(f"Error in get_all_objects_by_type_id: {e}")
            self.conn.rollback()
            return TechCardData()

    def get_all_possible_values_by_param_and_element(
        self, element_type_id: int, param_id: int
    ) -> TechCardData:
        """
        Уникальные значения параметра для типа элемента.
        paramsObjectControl + objectControl + paramsDefinition.
        """
        if not self.conn or not self.cursor:
            return TechCardData()
        try:
            self.cursor.execute(
                'SELECT "typeData" FROM "paramsDefinition" WHERE id = %s',
                (param_id,),
            )
            result = self.cursor.fetchone()
            if not result:
                return TechCardData()

            param_type = result["typeData"]
            self.cursor.execute("""
                SELECT DISTINCT
                    CASE
                        WHEN poc."valueInt" IS NOT NULL THEN poc."valueInt"::text
                        WHEN poc."valueDouble" IS NOT NULL THEN poc."valueDouble"::text
                        WHEN poc."valueString" IS NOT NULL THEN poc."valueString"
                        WHEN poc."valueBool" IS NOT NULL THEN poc."valueBool"::text
                    END AS value,
                    CASE
                        WHEN poc."valueInt" IS NOT NULL THEN 'integer'
                        WHEN poc."valueDouble" IS NOT NULL THEN 'double'
                        WHEN poc."valueString" IS NOT NULL THEN 'string'
                        WHEN poc."valueBool" IS NOT NULL THEN 'boolean'
                    END AS value_type
                FROM "paramsObjectControl" poc
                INNER JOIN "objectControl" oc ON poc."idObjectControl" = oc.id
                WHERE poc."idDefParams" = %s AND oc."idTypeControl" = %s
                ORDER BY value
            """, (param_id, element_type_id))
            all_values = self.cursor.fetchall()

            processed_values = []
            for item in all_values:
                value = item["value"]
                value_type = item["value_type"]
                if value is None:
                    continue
                try:
                    if param_type and param_type.lower() == "integer" and value_type == "integer":
                        processed_values.append(int(value))
                    elif param_type and param_type.lower() in ("double", "float", "real") and value_type in ("double", "integer"):
                        processed_values.append(float(value))
                    elif param_type and param_type.lower() == "boolean" and value_type == "boolean":
                        processed_values.append(value.lower() == "true")
                    elif param_type and param_type.lower() == "string":
                        processed_values.append(str(value))
                except (ValueError, TypeError):
                    continue

            unique_values = list(dict.fromkeys(processed_values))
            tech_card = TechCardData()
            tech_card.params = {param_id: unique_values}
            return tech_card
        except Exception as e:
            print(f"Error in get_all_possible_values_by_param_and_element: {e}")
            self.conn.rollback()
            return TechCardData()

    def get_params_for_element(self, element_id: int) -> TechCardData:
        """
        Все параметры и их значения для элемента, сгруппированные по блокам.
        """
        if not self.conn or not self.cursor:
            return TechCardData()
        try:
            # Сначала получаем тип объекта контроля и имя самого объекта
            self.cursor.execute("""
                SELECT oc.id, oc.name as object_name, oc."idTypeControl", toc.name as type_name
                FROM "objectControl" oc
                JOIN "typeOfControlledElement" toc ON oc."idTypeControl" = toc."Id"
                WHERE oc.id = %s
            """, (element_id,))
            
            type_result = self.cursor.fetchone()
            if not type_result:
                return TechCardData()  # Элемент не найден
            
            type_name = type_result["type_name"]
            object_name = type_result["object_name"]
            object_id = type_result["id"]
            
            # Определяем enum тип на основе имени из базы
            type_object = None
            if type_name.lower() == "пластина":
                type_object = TypeObjectControl.PLATE
            elif type_name.lower() == "труба":
                type_object = TypeObjectControl.PIPE
            else:
                type_object = type_name

            # Получаем все блоки
            self.cursor.execute('SELECT "blockId", name FROM blocks ORDER BY "blockId"')
            blocks_rows = self.cursor.fetchall()

            # Инициализируем словарь для результата
            blocks_dict = {}
            for block_row in blocks_rows:
                block_id = block_row["blockId"]
                block_name = block_row["name"]
                blocks_dict[block_id] = {
                    "name": block_name,
                    "params": {}
                }

            # Получаем параметры для элемента
            self.cursor.execute("""
                SELECT
                    pd.id AS param_id,
                    pd.name AS param_name,
                    pd."typeData",
                    pd."idBlock",
                    b."blockId",
                    b.name AS block_name,
                    poc."valueInt",
                    poc."valueDouble",
                    poc."valueString",
                    poc."valueBool"
                FROM "paramsObjectControl" poc
                JOIN "paramsDefinition" pd ON poc."idDefParams" = pd.id
                LEFT JOIN blocks b ON pd."idBlock" = b."blockId"
                WHERE poc."idObjectControl" = %s
                ORDER BY b."blockId" NULLS LAST, pd.name
            """, (element_id,))
            rows = self.cursor.fetchall()

            # Собираем все параметры для каждого блока
            for row in rows:
                block_id = row["blockId"] if row["blockId"] is not None else 1
                if block_id not in blocks_dict:
                    block_name = row["block_name"] if row["block_name"] else "Без блока"
                    blocks_dict[block_id] = {
                        "name": block_name,
                        "params": {}
                    }
                
                # Определяем значение параметра
                type_data = row["typeData"]
                v_int, v_double, v_string, v_bool = row["valueInt"], row["valueDouble"], row["valueString"], row["valueBool"]
                
                if type_data and type_data.lower() == "int" and v_int is not None:
                    value = v_int
                elif type_data and type_data.lower() == "double" and v_double is not None:
                    value = v_double
                elif type_data and type_data.lower() == "string" and v_string is not None:
                    value = v_string
                elif type_data and type_data.lower() == "bool" and v_bool is not None:
                    value = v_bool
                else:
                    value = v_int if v_int is not None else v_double if v_double is not None else v_string if v_string is not None else v_bool
                
                # Добавляем параметр в структуру
                param_id = row["param_id"]
                param_name = row["param_name"]
                if param_name is not None:
                    blocks_dict[block_id]["params"][param_id] = {
                        "name": param_name,
                        "val": value
                    }
            
            # Добавляем параметр "Объект контроля" в блок 1 как первый параметр
            # Используем специальный ID (например -1), чтобы он был первым при сортировке
            if 1 not in blocks_dict:
                blocks_dict[1] = {
                    "name": "Основной блок",
                    "params": {}
                }
            
            # Создаем значение с id и названием объекта
            object_control_value = {
                "id": object_id,
                "name": object_name
            }
            
            # Вставляем параметр "Объект контроля" первым в словарь
            # Для этого создаем новый OrderedDict
            params_block_1 = blocks_dict[1]["params"]
            
            # Создаем новый словарь с параметром "Объект контроля" первым
            new_params = {}
            new_params[0] = {
                "name": "Объект контроля",
                "val": object_control_value
            }
            
            # Добавляем остальные параметры
            new_params.update(params_block_1)
            blocks_dict[1]["params"] = new_params

            # Создаем TechCardData с типом
            tech_card = TechCardData(
                typeObjectControl=type_object,
                params=blocks_dict
            )

            self.cursor.execute("""SELECT
                    m."idMaterial",
                    m.name
                FROM material m
                ORDER BY m.name
            """)
                
            rows = self.cursor.fetchall()
            steel_names = [
                row['name']
                for row in rows
                if row.get('name')
            ]
            paramSt={
                'name':'Основной материал(марка стали)',
                'val':steel_names
                }
            tech_card.add_param_to_block("Объект контроля",paramSt)

            return tech_card
        except Exception as e:
            print(f"Error in get_params_for_element: {e}")
            self.conn.rollback()
            return TechCardData()
