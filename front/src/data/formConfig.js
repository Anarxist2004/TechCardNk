import api from '../services/api';

export const updateTechCard = (techCardData) => api.updateTechCard(techCardData);

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

      const cell = {
        name: param.name,
        val: value !== undefined && value !== '' ? value : param.value,
        ...(param.subtitle !== undefined && param.subtitle !== null && String(param.subtitle).trim() !== ''
          ? { subtitle: String(param.subtitle).trim() }
          : {}),
        options: Array.isArray(param.options) ? param.options : [],
        typeData: param.typeData || 'string',
        displayMode: param.displayMode || null,
      };

      if (param.hasVal2) {
        const value2 = paramValues2[compositeKey];
        cell.val2 = value2 !== undefined && value2 !== '' ? value2 : param.value2;
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
