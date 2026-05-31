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

        const hasVal2 = Object.prototype.hasOwnProperty.call(param, 'val2');
        const rawSubtitle = param.subtitle;

        const paramData = {
          id: paramId,
          name: param.name || `Параметр ${paramId}`,
          value: param.val,
          ...(hasVal2 ? { value2: param.val2, hasVal2: true } : {}),
          options: Array.isArray(param.options) ? param.options : [],
          typeData: param.typeData || 'string',
          displayMode: param.displayMode || null,
          selectedId: param.selectedId ?? null,
          canCreateOption: Boolean(param.canCreateOption),
          syncOnSelect: Boolean(param.syncOnSelect),
          readOnly: Boolean(param.readOnly),
          image: param.image || null,
          placeholder: param.placeholder ?? null,
          ...(rawSubtitle !== undefined && rawSubtitle !== null && String(rawSubtitle).trim() !== ''
            ? { subtitle: String(rawSubtitle).trim() }
            : {}),
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

function normalizeSavedUploadedImages(uploadedImages) {
  if (!uploadedImages || typeof uploadedImages !== 'object') {
    return {};
  }

  return Object.fromEntries(
    Object.entries(uploadedImages).map(([blockId, images]) => [
      blockId,
      Array.isArray(images)
        ? images
          .filter((image) => image && image.preview)
          .map((image, index) => ({
            id: image.id || `${blockId}-saved-${index}`,
            name: image.name || `Изображение ${index + 1}`,
            preview: image.preview,
          }))
        : [],
    ]),
  );
}

function normalizeSavedImagesList(images) {
  if (!Array.isArray(images)) {
    return [];
  }

  return images
    .filter((image) => image && image.preview)
    .map((image, index) => ({
      id: image.id || `overview-saved-${index}`,
      name: image.name || `Изображение ${index + 1}`,
      preview: image.preview,
      createdAt: image.createdAt || image.created_at || null,
      fileName: image.fileName || null,
      mimeType: image.mimeType || null,
    }));
}

function transformSavedTechCardResponse(data) {
  if (!data) {
    return null;
  }

  const snapshot = data.card_data && typeof data.card_data === 'object'
    ? data.card_data
    : {};

  return {
    id: data.id ?? null,
    name: data.name || snapshot.cardName || '',
    createdAt: data.created_at ?? null,
    updatedAt: data.updated_at ?? null,
    cardName: snapshot.cardName || data.name || '',
    techCard: transformBlocksResponse(snapshot.techCard || {}),
    customFields: snapshot.customFields && typeof snapshot.customFields === 'object'
      ? snapshot.customFields
      : {},
    uploadedImages: normalizeSavedUploadedImages(snapshot.uploadedImages),
    overview: snapshot.overview && typeof snapshot.overview === 'object'
      ? {
        photographerName: snapshot.overview.photographerName || '',
        photographerPosition: snapshot.overview.photographerPosition || '',
        company: snapshot.overview.company || '',
        weldImages: normalizeSavedImagesList(snapshot.overview.weldImages),
      }
      : null,
  };
}

async function loadTechCardTemplate(methodology = 0) {
  const data = await postRequest('template', {
    methodology: normalizeMethodology(methodology),
  });

  return transformBlocksResponse(data);
}

const api = {
  getTemplate: loadTechCardTemplate,
  getFullTechCard: loadTechCardTemplate,

  updateTechCard: async (techCardData) => {
    const data = await postRequest('updateTechCard', { techCard: techCardData });
    return transformBlocksResponse(data);
  },

  saveTechCard: (payload) => postRequest('saveTechCard', payload),

  getCurrentUser: () => fetch('/api/auth/me', { credentials: 'same-origin' }).then(async (response) => {
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.detail || 'Ошибка загрузки пользователя');
    }
    return data;
  }),

  listSavedTechCards: async () => {
    const data = await postRequest('listSavedTechCards', {});
    return Array.isArray(data)
      ? data.map((item) => ({
        id: item.id,
        name: item.name || `Техкарта #${item.id}`,
        createdAt: item.created_at ?? null,
        updatedAt: item.updated_at ?? null,
      }))
      : [];
  },

  getSavedTechCard: async (id) => {
    const data = await postRequest('getSavedTechCard', { id });
    return transformSavedTechCardResponse(data);
  },

  createParamOption: (payload) => postRequest('createParamOption', payload),
};

export default api;
