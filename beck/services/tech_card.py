import json
from typing import Optional, Dict, Any
from typing import Union

from enum import StrEnum
class TypeObjectControl(StrEnum):
    PLATE="пластина"
    PIPE="труба"
    
class TechCardData:
    def __init__(
        self,
        typeObjectControl: Optional[TypeObjectControl] = None,
        params: Optional[Dict[str, Dict[str, Any]]] = None
    ):
        self.type = typeObjectControl
        self.params = params or {}

    def get(self, key: str):
        return self.params.get(key)

    def set(self, key: str, value):
        self.params[key] = value


    def getTypeObjectControl(self,)->TypeObjectControl:
        return self.type
    
    def to_dict(self) -> Dict:
        return {
            "currentParams": self.params,
    }

    def _to_json_dict(self) -> Dict[str, Any]:
        type_val = self.type.value if hasattr(self.type, "value") else self.type
        return {
            "type": type_val,
            "params": self.params,
        }

    def __str__(self) -> str:
        return json.dumps(
            self._to_json_dict(),
            ensure_ascii=False,
            indent=2,
        )

    def serialise(self) -> str:
        return json.dumps(
            self._to_json_dict(),
            ensure_ascii=False,
            indent=2,
        )

    def from_jsonDeSerialise(self, data: str | Dict[str, Any]) -> "TechCardData":
        if isinstance(data, str):
            data = json.loads(data)  # превращаем JSON-строку в словарь

        type_val = data.get("type")
        params = data.get("params", {})


        self.typeObjectControl=type_val
        self.params=params
    
    def has_block_and_param(self,block_name: str,param_name: str) -> bool:
        for block in self.params.values():
            if block.get("name") == block_name:
                # блок найден
                params = block.get("params", {})
                for param in params.values():
                    if param.get("name") == param_name:
                        return True
                return False

        return False

    def has_block(self, block_name: str) -> bool:
        return any(
            block.get("name") == block_name
            for block in self.params.values()
        )        

    def _find_free_id(self, items: Dict[Any, Any]) -> int:
        used_ids = set()

        for k in items.keys():
            if isinstance(k, int):
                used_ids.add(k)
            elif isinstance(k, str) and k.isdigit():
                used_ids.add(int(k))

        new_id = 1
        while new_id in used_ids:
            new_id += 1

        return new_id

    def add_param_to_block(
        self,
        block_name: str,
        param: Dict[str, Any]
    ) -> bool:
        if "name" not in param:
            raise ValueError("param должен содержать ключ 'name'")

        for block in self.params.values():
            if block.get("name") == block_name:
                params = block.setdefault("params", {})

                # проверяем на дубликат
                for existing in params.values():
                    if existing.get("name") == param["name"]:
                        return False

                free_id = self._find_free_id(params)
                params[free_id] = dict(param)
                return True

        return False
    
    def insert_param_to_block(self, block_name: str, insert_id: int, param: Dict[str, Any]) -> bool:
        if "name" not in param:
            raise ValueError("param должен содержать ключ 'name'")

        for block in self.params.values():
            if block.get("name") != block_name:
                continue

            params = block.setdefault("params", {})

            # Проверка на дубликат по имени
            for existing in params.values():
                if existing.get("name") == param["name"]:
                    return False

            idx = insert_id
            to_move = []

            # Находим цепочку занятых ключей подряд, начиная с insert_id
            while idx in params:
                to_move.append(idx)
                idx += 1

            # Сдвигаем только цепочку занятых ключей
            for k in reversed(to_move):
                params[k + 1] = params.pop(k)

            # Вставляем новый параметр
            params[insert_id] = dict(param)
            return True

        return False
    
    # def insert_param_to_block_reWrite(
    #     self,
    #     block_name: str,
    #     insert_id: Union[int, str],
    #     param: Dict[str, Any]
    # ) -> bool:
    #     if "name" not in param:
    #         raise ValueError("param должен содержать ключ 'name'")

    #     # --- нормализация insert_id ---
    #     try:
    #         if isinstance(insert_id, str):
    #             if "." in insert_id:
    #                 raise ValueError
    #             insert_id = int(insert_id)
    #         else:
    #             insert_id = int(insert_id)
    #     except (ValueError, TypeError):
    #         raise ValueError(f"insert_id должен быть целым числом, получено: {insert_id!r}")

    #     for block in self.params.values():
    #         if block.get("name") != block_name:
    #             continue

    #         params = block.setdefault("params", {})

    #         # --- собираем только int-ключи ---
    #         int_keys = [k for k in params.keys() if isinstance(k, int)]

    #         # --- ищем параметр с тем же name ---
    #         old_key = None
    #         for k in int_keys:
    #             if params[k].get("name") == param["name"]:
    #                 old_key = k
    #                 break

    #         # --- если параметр уже есть — удаляем ---
    #         if old_key is not None:
    #             params.pop(old_key)
    #             int_keys.remove(old_key)

    #             # если удалённый был левее точки вставки — сдвигаем insert_id
    #             if old_key < insert_id:
    #                 insert_id -= 1

    #         # --- сдвигаем хвост вправо начиная с insert_id ---
    #         for k in sorted((k for k in int_keys if k >= insert_id), reverse=True):
    #             params[k + 1] = params.pop(k)

    #         # --- вставляем новый параметр ---
    #         params[insert_id] = dict(param)

    #         return True

    #     return False
    
    def _id_to_sort_key(self, key) -> tuple:
        """
        Преобразует id:
        1        -> (1,)
        "2"      -> (2,)
        "1.2"    -> (1, 2)
        "1.2.10" -> (1, 2, 10)
        """
        if isinstance(key, int):
            return (key,)

        if isinstance(key, str):
            try:
                return tuple(int(part) for part in key.split("."))
            except ValueError:
                pass

        # fallback для странных ключей
        return (float("inf"),)
    
    def sort_all_params(self) -> None:
        for block in self.params.values():
            params = block.get("params")
            if not isinstance(params, dict):
                continue

            sorted_items = sorted(
                params.items(),
                key=lambda item: self._id_to_sort_key(item[0])
            )

            block["params"] = dict(sorted_items)

    def get_param_value(self,block_name: str,param_name: str) -> Optional[Any]:
        for block in self.params.values():
            if block.get("name") == block_name:
                params = block.get("params", {})
                for param in params.values():
                    if param.get("name") == param_name:
                        return param.get("val")
                return None
        return None
    
    def _parse_id(self, key) -> list[int]:
        if isinstance(key, int):
            return [key]
        if isinstance(key, str):
            return [int(p) for p in key.split(".") if p.isdigit()]
        return []
    
    def _same_level(self, a: list[int], b: list[int]) -> bool:
        return len(a) == len(b)
    
    def change_param_id_by_name_autoshift(
        self,
        block_name: str,
        param_name: str,
        new_id: Union[int, str]
    ) -> bool:
        target_id = self._parse_id(new_id)

        for block in self.params.values():
            if block.get("name") != block_name:
                continue

            params = block.get("params", {})
            old_key = None
            old_id = None

            # ищем параметр по имени
            for k, v in params.items():
                if v.get("name") == param_name:
                    old_key = k
                    old_id = self._parse_id(k)
                    break

            if old_key is None:
                return False  # параметр не найден

            # проверка: параметр уже на нужном месте
            if old_id == target_id:
                return True  # ничего не делаем

            # собираем id того же уровня
            level_keys = []
            for k in params.keys():
                parsed = self._parse_id(k)
                if self._same_level(parsed, target_id):
                    level_keys.append((k, parsed))

            # сдвигаем в обратном порядке
            for k, parsed in sorted(level_keys, key=lambda x: x[1], reverse=True):
                if parsed >= target_id:
                    new_key = ".".join(str(p) for p in (parsed[:-1] + [parsed[-1] + 1]))
                    params[new_key] = params.pop(k)

            # вставляем параметр
            params[".".join(str(p) for p in target_id)] = params.pop(old_key)

            # сортируем после операции
            sorted_items = sorted(
                params.items(), key=lambda item: self._id_to_sort_key(item[0])
            )
            block["params"] = dict(sorted_items)
            return True

        return False
    
    def hasSpecParam(self,block_name: str,param_name: str):
        val = self.get_param_value(block_name, param_name)
    
        # если пустое поле (None) или массив (list/tuple) — False
        if val is None or isinstance(val, (list, tuple)):
            return False
        
        # иначе не массив — True
        return True
        









    def insert_param_to_block_reWrite(
    self,
    block_name: str,
    insert_id: Union[int, str],
    param: Dict[str, Any]
) -> bool:
        if "name" not in param:
            raise ValueError("param должен содержать ключ 'name'")

        # --- нормализация insert_id ---
        # Поддерживаем int, float и строки типа "4.2"
        if isinstance(insert_id, (int, float)):
            insert_id_str = str(insert_id)
        else:
            insert_id_str = str(insert_id)
        
        # Проверяем формат: должны быть только цифры и точки
        if not all(part.isdigit() for part in insert_id_str.split('.')):
            raise ValueError(
                f"insert_id должен быть числом или многоуровневым числом, получено: {insert_id!r}"
            )

        # Для сравнений используем tuple из int частей
        insert_id_tuple = tuple(int(part) for part in insert_id_str.split('.'))

        for block in self.params.values():
            if block.get("name") != block_name:
                continue

            params = block.setdefault("params", {})

            # --- ищем параметр с тем же name ---
            old_key = None
            for k in params.keys():
                if params[k].get("name") == param["name"]:
                    old_key = k
                    break

            # --- если параметр уже есть — удаляем ---
            if old_key is not None:
                params.pop(old_key)
                
                # Сравниваем ключи
                old_key_tuple = self._key_to_tuple(old_key)
                if self._compare_tuples(old_key_tuple, insert_id_tuple) < 0:
                    # old_key < insert_id, нужно уменьшить insert_id
                    insert_id_tuple = self._decrement_tuple(insert_id_tuple, old_key_tuple)

            # --- сдвигаем хвост вправо ---
            keys_to_move = []
            for k in params.keys():
                key_tuple = self._key_to_tuple(k)
                if self._compare_tuples(key_tuple, insert_id_tuple) >= 0:
                    keys_to_move.append((k, key_tuple))
            
            # Сортируем по убыванию для правильного сдвига
            keys_to_move.sort(key=lambda x: x[1], reverse=True)
            
            for old_k, old_tuple in keys_to_move:
                new_tuple = self._increment_tuple(old_tuple, insert_id_tuple)
                new_k = self._tuple_to_key(new_tuple)
                params[new_k] = params.pop(old_k)

            # --- вставляем новый параметр ---
            new_key = self._tuple_to_key(insert_id_tuple)
            params[new_key] = dict(param)

            return True

        return False

    def _key_to_tuple(self, key: Any) -> tuple:
        """Преобразует ключ в tuple."""
        if isinstance(key, (int, float)):
            return (int(key),)
        elif isinstance(key, str):
            return tuple(int(part) for part in key.split('.'))
        else:
            return (int(key),)

    def _tuple_to_key(self, t: tuple) -> str:
        """Преобразует tuple в строковый ключ."""
        return '.'.join(str(part) for part in t)

    def _compare_tuples(self, t1: tuple, t2: tuple) -> int:
        """Сравнивает два tuple как многоуровневые числа."""
        for a, b in zip(t1, t2):
            if a != b:
                return -1 if a < b else 1
        return 0 if len(t1) == len(t2) else (-1 if len(t1) < len(t2) else 1)

    def _increment_tuple(self, key_tuple: tuple, insert_tuple: tuple) -> tuple:
        """Увеличивает key_tuple на уровне insert_tuple."""
        result = list(key_tuple)
        level = min(len(insert_tuple), len(key_tuple)) - 1
        if level >= 0:
            result[level] += 1
            # Отрезаем хвост после увеличенного уровня
            return tuple(result[:level + 1])
        return key_tuple

    def _decrement_tuple(self, insert_tuple: tuple, old_tuple: tuple) -> tuple:
        """Уменьшает insert_tuple, если old_tuple был меньше."""
        result = list(insert_tuple)
        for level in range(min(len(insert_tuple), len(old_tuple))):
            if old_tuple[level] < insert_tuple[level]:
                result[level] -= 1
                # Если стало 0 и не первый уровень - убираем
                if result[level] == 0 and level > 0:
                    result.pop(level)
                break
        return tuple(result)