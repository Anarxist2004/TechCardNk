const API_URL = '/techcard';

const normalizeMethodology = (methodology = 0) => Number.parseInt(methodology, 10) || 0;

async function postRequest(endpoint, payload = {}) {
  const response = await fetch(`${API_URL}/${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const text = await response.text();

  try {
    return JSON.parse(JSON.parse(text));
  } catch {
    return JSON.parse(text);
  }
}

const sortCompositeIds = (ids) => ids.sort((leftId, rightId) => {
  const leftParts = String(leftId).split('.').map((part) => Number.parseInt(part, 10) || 0);
  const rightParts = String(rightId).split('.').map((part) => Number.parseInt(part, 10) || 0);
  const maxLength = Math.max(leftParts.length, rightParts.length);

  for (let index = 0; index < maxLength; index += 1) {
    const leftValue = leftParts[index] ?? 0;
    const rightValue = rightParts[index] ?? 0;

    if (leftValue !== rightValue) {
      return leftValue - rightValue;
    }
  }

  return 0;
});

function transformBlocksResponse(data) {
  if (!data || !data.params) {
    return { type: null, blocks: [], flatParams: [] };
  }

  const blocks = [];
  const flatParams = [];
  const sortedBlockIds = Object.keys(data.params).sort(
    (leftId, rightId) => Number.parseInt(leftId, 10) - Number.parseInt(rightId, 10),
  );

  sortedBlockIds.forEach((blockId) => {
    const block = data.params[blockId];
    if (!block) {
      return;
    }

    const blockData = {
      id: blockId,
      name: block.name || `Блок ${blockId}`,
      params: [],
    };

    if (block.params && typeof block.params === 'object') {
      sortCompositeIds(Object.keys(block.params)).forEach((paramId) => {
        const param = block.params[paramId];
        if (!param) {
          return;
        }

        const paramData = {
          id: paramId,
          name: param.name || `Параметр ${paramId}`,
          value: param.val,
          options: Array.isArray(param.options) ? param.options : [],
          typeData: param.typeData || 'string',
          displayMode: param.displayMode || null,
          selectedId: param.selectedId ?? null,
          canCreateOption: Boolean(param.canCreateOption),
          image: param.image || null,
          blockId,
          blockName: block.name,
        };

        blockData.params.push(paramData);
        flatParams.push(paramData);
      });
    }

    blocks.push(blockData);
  });

  return { type: data.type, blocks, flatParams };
}

const api = {
  getFullTechCard: async (methodology = 0) => {
    const data = await postRequest('elementParamValue', {
      idElement: 0,
      methodology: normalizeMethodology(methodology),
    });

    return transformBlocksResponse(data);
  },

  updateTechCard: async (techCardData) => {
    const data = await postRequest('updateTechCard', { techCard: techCardData });
    return transformBlocksResponse(data);
  },

  createParamOption: (payload) => postRequest('createParamOption', payload),
};

export default api;
