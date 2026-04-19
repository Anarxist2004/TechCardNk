import api from '../services/api';

export const updateTechCard = (techCardData) => api.updateTechCard(techCardData);

const resolveParamOptions = (param) => {
  if (Array.isArray(param.options) && param.options.length > 0) {
    return param.options;
  }

  if (Array.isArray(param.value) && param.value.length > 0) {
    return param.value;
  }

  return [];
};

export const buildTechCardPayload = (
  type,
  methodology,
  blocks,
  paramValues,
  selectedOptionIds = {},
  paramValues2 = {},
) => {
  const params = {};

  blocks.forEach((block) => {
    params[block.id] = {
      name: block.name,
      params: {},
    };

    block.params.forEach((param) => {
      const compositeKey = `${block.id}.${param.id}`;
      const value = paramValues[compositeKey];
      const selectedId = selectedOptionIds[compositeKey];
      const hasValueOverride = Object.prototype.hasOwnProperty.call(paramValues, compositeKey);

      const cell = {
        name: param.name,
        val: hasValueOverride ? value : param.value,
        ...(param.subtitle !== undefined && param.subtitle !== null && String(param.subtitle).trim() !== ''
          ? { subtitle: String(param.subtitle).trim() }
          : {}),
        ...(Object.prototype.hasOwnProperty.call(param, 'placeholder')
          ? { placeholder: param.placeholder }
          : {}),
        options: resolveParamOptions(param),
        typeData: param.typeData || 'string',
        displayMode: param.displayMode || null,
        ...(Object.prototype.hasOwnProperty.call(param, 'from_welded_joint_params_db')
          ? { from_welded_joint_params_db: param.from_welded_joint_params_db }
          : {}),
        ...(Object.prototype.hasOwnProperty.call(param, 'welded_joint_binding')
          ? { welded_joint_binding: param.welded_joint_binding }
          : {}),
      };

      if (param.hasVal2) {
        const value2 = paramValues2[compositeKey];
        const hasValue2Override = Object.prototype.hasOwnProperty.call(paramValues2, compositeKey);
        cell.val2 = hasValue2Override ? value2 : param.value2;
      }

      params[block.id].params[param.id] = cell;

      if (selectedId !== undefined && selectedId !== null && selectedId !== '') {
        params[block.id].params[param.id].selectedId = String(selectedId);
      }
    });
  });

  return {
    methodology: Number.parseInt(methodology, 10) || 0,
    type,
    params,
  };
};
