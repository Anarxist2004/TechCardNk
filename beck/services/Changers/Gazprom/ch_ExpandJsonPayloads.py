from services.Interfaces.i_dataChanger import IDataChanger
from services.tech_card import TechCardData


class ExpandJsonPayloads(IDataChanger):
    TARGET_BLOCKS = (
        "Расшифровка радиографии",
        "Оценка качества",
        "Допустимые включения",
    )

    def changeData(self, data: TechCardData):
        for block in data.params.values():
            block_name = block.get("name", "")
            if not any(block_name.startswith(prefix) for prefix in self.TARGET_BLOCKS):
                continue

            params = block.get("params", {})
            if not isinstance(params, dict):
                continue

            expanded_params = {}
            next_id = 1

            for _, param in params.items():
                param_name = param.get("name")
                param_value = param.get("val")
                param_meta = {
                    key: value
                    for key, value in param.items()
                    if key not in {"name", "val"}
                }

                if isinstance(param_value, (dict, list)):
                    base_id = next_id
                    expanded_params[base_id] = {
                        "name": param_name,
                        "val": "См. подпункты",
                        **param_meta,
                    }
                    next_id += 1

                    for suffix, nested_name, nested_value in self._expand_payload(param_value):
                        expanded_params[f"{base_id}.{suffix}"] = {
                            "name": nested_name,
                            "val": nested_value,
                            **param_meta,
                        }
                    continue

                expanded_params[next_id] = {
                    "name": param_name,
                    "val": param_value,
                    **param_meta,
                }
                next_id += 1

            block["params"] = expanded_params

    def _expand_payload(self, payload, prefix: str = ""):
        result = []

        if isinstance(payload, dict):
            for index, (key, value) in enumerate(payload.items(), start=1):
                current_prefix = f"{prefix}{index}"
                if isinstance(value, (dict, list)):
                    result.append((current_prefix, str(key), "См. подпункты"))
                    result.extend(self._expand_payload(value, f"{current_prefix}."))
                else:
                    result.append((current_prefix, str(key), self._format_scalar(value)))
            return result

        if isinstance(payload, list):
            for index, value in enumerate(payload, start=1):
                current_prefix = f"{prefix}{index}"
                label = f"Пункт {index}"
                if isinstance(value, (dict, list)):
                    result.append((current_prefix, label, "См. подпункты"))
                    result.extend(self._expand_payload(value, f"{current_prefix}."))
                else:
                    result.append((current_prefix, label, self._format_scalar(value)))
            return result

        return result

    def _format_scalar(self, value):
        if isinstance(value, bool):
            return "Да" if value else "Нет"
        return value
