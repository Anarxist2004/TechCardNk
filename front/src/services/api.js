// API сервис для работы с backend
// Используем относительный путь - Vite proxy перенаправит на бэкенд
const API_URL = '/techcard';

/**
 * Выполняет POST запрос к backend
 * @param {string} endpoint - эндпоинт API
 * @param {object} payload - тело запроса
 */
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
  // Backend возвращает JSON как строку, нужно распарсить дважды
  try {
    return JSON.parse(JSON.parse(text));
  } catch {
    // Если одинарный JSON
    return JSON.parse(text);
  }
}

/**
 * Преобразует ответ с типами объектов контроля
 * Формат ответа: { type: { "0": "Пластина", "1": "Труба" }, params: {} }
 * Результат: [{ id: "0", name: "Пластина" }, { id: "1", name: "Труба" }]
 */
function transformTypesResponse(data) {
  if (!data) return [];
  
  // type содержит { id: name, id2: name2, ... }
  // Может быть в data.type или напрямую в data (если это объект с типами)
  const typeData = data.type || data;
  
  if (typeof typeData !== 'object' || typeData === null) return [];
  
  return Object.entries(typeData)
    .filter(([key]) => key !== 'params' && key !== 'type') // Исключаем служебные ключи
    .map(([id, name]) => ({ id, name }));
}

/**
 * Преобразует ответ с блочной структурой параметров
 * Формат ответа:
 * {
 *   type: "пластина" | "труба",
 *   params: {
 *     "block_id": {
 *       name: "Название блока",
 *       params: {
 *         "param_id": { name: "Название параметра", val: значение }
 *       }
 *     }
 *   }
 * }
 * Результат: { type, blocks: [...], flatParams: [...] }
 * 
 * Параметры могут иметь составные ID типа "1.0", "1.2", "1.4.1", "1.4.2"
 */
function transformBlocksResponse(data) {
  if (!data || !data.params) return { type: null, blocks: [], flatParams: [] };

  const blocks = [];
  const flatParams = [];

  // Сортируем блоки по ID (числовая сортировка)
  const sortedBlockIds = Object.keys(data.params).sort((a, b) => parseInt(a) - parseInt(b));

  sortedBlockIds.forEach((blockId) => {
    const block = data.params[blockId];
    if (!block) return;
    
    const blockData = {
      id: blockId,
      name: block.name || `Блок ${blockId}`,
      params: []
    };

    if (block.params && typeof block.params === 'object') {
      // Сортируем параметры по составным ID типа "1.0", "1.2", "1.4.1"
      const sortedParamIds = Object.keys(block.params).sort((a, b) => {
        const parseId = (id) => {
          const strId = String(id);
          return strId.split('.').map(part => parseInt(part) || 0);
        };
        const aParts = parseId(a);
        const bParts = parseId(b);
        for (let i = 0; i < Math.max(aParts.length, bParts.length); i++) {
          const aVal = aParts[i] !== undefined ? aParts[i] : 0;
          const bVal = bParts[i] !== undefined ? bParts[i] : 0;
          if (aVal !== bVal) return aVal - bVal;
        }
        return 0;
      });

      sortedParamIds.forEach((paramId) => {
        const param = block.params[paramId];
        if (!param) return;
        
        const paramData = {
          id: paramId,
          name: param.name || `Параметр ${paramId}`,
          value: param.val,
          image: param.image || null,
          blockId: blockId,
          blockName: block.name
        };
        blockData.params.push(paramData);
        flatParams.push(paramData);
      });
    }

    blocks.push(blockData);
  });

  return { type: data.type, blocks, flatParams };
}

/**
 * Извлекает объекты контроля из блочного ответа
 * Объекты контроля находятся в блоке 1, параметр с id "0" и name "Объект контроля"
 * Формат: params["1"]["params"]["0"]["val"] = { "1": "Труба Д273x8; АТС-0001-21", ... }
 */
function extractObjectsFromBlocks(blocksData) {
  // Ищем блок 1 (Объект контроля)
  const block1 = blocksData.blocks.find(b => b.id === "1" || b.id === 1);
  if (!block1) return [];

  // Ищем параметр "Объект контроля" (обычно id = "0")
  const objectControlParam = block1.params.find(p => 
    p.name === "Объект контроля" || p.id === "0" || p.id === 0
  );
  
  if (!objectControlParam || !objectControlParam.value) return [];

  // value - объект { id: name, ... } например { "1": "Труба Д273x8; АТС-0001-21" }
  if (typeof objectControlParam.value === 'object' && !Array.isArray(objectControlParam.value)) {
    // Проверяем, не является ли это объектом с id и name (для elementParamValue)
    if (objectControlParam.value.id !== undefined && objectControlParam.value.name !== undefined) {
      return [{ id: String(objectControlParam.value.id), name: objectControlParam.value.name }];
    }
    // Иначе это словарь { "1": "Name1", "2": "Name2" }
    return Object.entries(objectControlParam.value).map(([id, name]) => ({ id, name }));
  }

  return [];
}

/**
 * Преобразует блоки в плоский список параметров с typeData
 * Для совместимости с текущим UI
 */
function extractParamsFromBlocks(blocksData) {
  const params = [];

  blocksData.blocks.forEach(block => {
    block.params.forEach(param => {
      // Определяем typeData по значению
      let typeData = 'string';
      if (typeof param.value === 'number') {
        typeData = Number.isInteger(param.value) ? 'int' : 'double';
      } else if (typeof param.value === 'boolean') {
        typeData = 'bool';
      } else if (Array.isArray(param.value)) {
        // Массив значений - определяем тип по первому элементу
        if (param.value.length > 0) {
          const firstVal = param.value[0];
          if (typeof firstVal === 'number') {
            typeData = Number.isInteger(firstVal) ? 'int' : 'double';
          }
        }
      }

      params.push({
        id: param.id,
        name: param.name,
        typeData: typeData,
        value: param.value,
        blockId: param.blockId,
        blockName: param.blockName
      });
    });
  });

  return params;
}

export const api = {
  /**
   * Получить типы объектов контроля (например: Пластина, Труба)
   * Эндпоинт: POST /techcard/object
   */
  getObjectTypes: async () => {
    const data = await postRequest('object', {});
    return transformTypesResponse(data);
  },

  /**
   * Получить элементы (объекты контроля) по ID типа объекта
   * Эндпоинт: POST /techcard/element
   * @param {number} typeId - ID типа объекта
   */
  getElements: async (typeId) => {
    console.log('API: getElements, typeId:', typeId);
    const data = await postRequest('element', { type: parseInt(typeId) });
    console.log('API: ответ от element:', data);
    const blocksData = transformBlocksResponse(data);
    console.log('API: blocksData:', blocksData);
    const objects = extractObjectsFromBlocks(blocksData);
    console.log('API: извлеченные объекты контроля:', objects);
    return objects;
  },

  /**
   * Получить параметры для типа элемента (без значений)
   * Эндпоинт: POST /techcard/elementParams
   * @param {number} typeId - ID типа элемента
   * @returns {Promise<Array<{id: string, name: string, typeData: string}>>}
   */
  getElementParams: async (typeId) => {
    const data = await postRequest('elementParams', { idElement: parseInt(typeId) });
    const blocksData = transformBlocksResponse(data);
    return extractParamsFromBlocks(blocksData);
  },

  /**
   * Получить параметры и значения для конкретного элемента (объекта контроля)
   * Эндпоинт: POST /techcard/elementParamValue
   * @param {number|string} elementId - ID элемента (объекта контроля) из таблицы objectControl
   * @returns {Promise<{type, blocks, flatParams}>}
   */
  getElementParamsWithValues: async (elementId) => {
    // Преобразуем в число, если это строка
    const numericId = typeof elementId === 'string' ? parseInt(elementId, 10) : elementId;
    
    // Проверка на NaN
    if (isNaN(numericId) || numericId === null || numericId === undefined) {
      console.error('API: getElementParamsWithValues - невалидный ID:', elementId);
      return { type: null, blocks: [], flatParams: [] };
    }
    
    console.log('API: getElementParamsWithValues, idElement:', numericId);
    const data = await postRequest('elementParamValue', { idElement: numericId });
    console.log('API: ответ от elementParamValue:', data);
    return transformBlocksResponse(data);
  },

  /**
   * Получить стандартные значения для параметра
   * Использует ответ elementParamValue и извлекает значения из блоков
   * @param {number} elementId - ID элемента
   * @param {string} paramId - ID параметра
   */
  getParamStandardValues: async (elementId, paramId) => {
    const data = await postRequest('elementParamValue', { idElement: parseInt(elementId) });
    const blocksData = transformBlocksResponse(data);

    // Ищем параметр по ID
    for (const block of blocksData.blocks) {
      const param = block.params.find(p => p.id === paramId || p.id === String(paramId));
      if (param && Array.isArray(param.value)) {
        return param.value;
      }
    }
    return [];
  },

  /**
   * Обновить технологическую карту (пропустить через PipeLine)
   * Эндпоинт: POST /techcard/updateTechCard
   * @param {object} techCardData - данные тех. карты в формате TechCardData
   * @returns {Promise<{type, blocks, flatParams}>}
   */
  updateTechCard: async (techCardData) => {
    const data = await postRequest('updateTechCard', { techCard: techCardData });
    return transformBlocksResponse(data);
  },

  /**
   * Получить сырые данные (без преобразования)
   */
  raw: {
    getObjectTypes: () => postRequest('object', {}),
    getElements: (typeId) => postRequest('element', { type: parseInt(typeId) }),
    getElementParams: (typeId) => postRequest('elementParams', { idElement: parseInt(typeId) }),
    getElementParamsWithValues: (elementId) => postRequest('elementParamValue', { idElement: parseInt(elementId) }),
    updateTechCard: (techCardData) => postRequest('updateTechCard', { techCard: techCardData }),
  }
};

export default api;
