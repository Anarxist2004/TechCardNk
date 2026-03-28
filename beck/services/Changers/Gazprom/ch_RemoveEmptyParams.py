from services.Interfaces.i_dataChanger import IDataChanger
from services.tech_card import TechCardData


class RemoveEmptyParams(IDataChanger):
    def changeData(self, data: TechCardData):
        empty_blocks = []

        for block_id, block in data.params.items():
            params = block.get("params", {})
            if not isinstance(params, dict):
                continue

            cleaned_params = {}
            for param_id, param in params.items():
                if self._has_value(param):
                    cleaned_params[param_id] = param

            block["params"] = cleaned_params
            if len(cleaned_params) == 0:
                empty_blocks.append(block_id)

        for block_id in empty_blocks:
            data.params.pop(block_id, None)

    def _has_value(self, param: dict) -> bool:
        if param.get("image"):
            return True

        options = param.get("options")
        if isinstance(options, (list, tuple, set)):
            return len(options) > 0

        value = param.get("val")
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip() != ""
        if isinstance(value, (list, dict, tuple, set)):
            return len(value) > 0
        return True
