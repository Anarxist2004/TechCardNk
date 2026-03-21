import api from '../services/api';

export const updateTechCard = (techCardData) => api.updateTechCard(techCardData);

export const buildTechCardPayload = (
  type,
  methodology,
  blocks,
  paramValues,
  selectedOptionIds = {},
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

      params[block.id].params[param.id] = {
        name: param.name,
        val: value !== undefined && value !== '' ? value : param.value,
        options: Array.isArray(param.options) ? param.options : [],
        typeData: param.typeData || 'string',
        displayMode: param.displayMode || null,
      };

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
