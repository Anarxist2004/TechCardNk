// Конфигурация формы с загрузкой данных из backend
import api from '../services/api';

// Fallback данные на случай, если backend недоступен
const fallbackConfig = {
  objectTypes: [
    { id: "1", name: "Пластина", icon: "square", description: "Плоские сварные соединения" },
    { id: "2", name: "Труба", icon: "circle", description: "Трубопроводные сварные соединения" }
  ],
  jointTypes: {
    "1": [{ id: "butt", name: "Стыковое", description: "Стыковое сварное соединение пластин" }],
    "2": [
      { id: "ring", name: "Кольцевое", description: "Кольцевой сварной шов трубы" },
      { id: "butt", name: "Стыковое", description: "Стыковое сварное соединение труб" }
    ]
  },
  dimensionFields: {
    "1": [
      { id: "thickness", label: "Толщина, S, мм", type: "number", required: true },
      { id: "length", label: "Длина, мм", type: "number", required: true },
      { id: "width", label: "Ширина, мм", type: "number", required: true }
    ],
    "2": [
      { id: "diameter", label: "Наружный диаметр трубы, мм", type: "number", required: true },
      { id: "thickness", label: "Толщина стенки, S, мм", type: "number", required: true }
    ]
  },
  sections: []
};

// Кэш для загруженных данных
let cachedConfig = null;
let cachedBlocks = {}; // Кэш блоков по elementId

/**
 * Загрузка конфигурации формы с backend
 */
export const fetchFormConfig = async () => {
  try {
    // Загружаем типы объектов с backend
    const objectTypes = await api.getObjectTypes();
    
    // Добавляем иконки и описания для типов объектов
    const enrichedObjectTypes = objectTypes.map(obj => ({
      ...obj,
      icon: obj.name.toLowerCase().includes('пластин') ? 'square' : 'circle',
      description: obj.name.toLowerCase().includes('пластин') 
        ? 'Плоские сварные соединения' 
        : 'Трубопроводные сварные соединения'
    }));

    cachedConfig = {
      objectTypes: enrichedObjectTypes,
      jointTypes: fallbackConfig.jointTypes,
      dimensionFields: fallbackConfig.dimensionFields,
      sections: fallbackConfig.sections
    };

    return cachedConfig;
  } catch (error) {
    console.error('Ошибка загрузки конфигурации с backend, используем fallback:', error);
    cachedConfig = fallbackConfig;
    return fallbackConfig;
  }
};

/**
 * Получение элементов (объектов контроля) по ID типа объекта
 * Загружает данные с backend
 */
export const getElements = async (objectTypeId, methodology = 0) => {
  try {
    const elements = await api.getElements(parseInt(objectTypeId), methodology);
    if (elements && elements.length > 0) {
      return elements.map(el => ({
        ...el,
        description: `Объект контроля: ${el.name}`
      }));
    }
  } catch (error) {
    console.error('Ошибка загрузки элементов:', error);
  }
  
  // Fallback
  return fallbackConfig.jointTypes[objectTypeId] || [];
};

/**
 * Получение параметров и значений для конкретного элемента (объекта контроля)
 * Возвращает данные в блочной структуре
 * @param {number} elementId - ID элемента (объекта контроля)
 * @returns {Promise<{type, blocks, flatParams}>}
 */
export const getElementData = async (elementId, methodology = 0) => {
  try {
    const data = await api.getElementParamsWithValues(parseInt(elementId), methodology);
    // Кэшируем блоки
    cachedBlocks[elementId] = data;
    return data;
  } catch (error) {
    console.error('Ошибка загрузки данных элемента:', error);
    return { type: null, blocks: [], flatParams: [] };
  }
};

/**
 * Получение полей размеров (параметров) по ID типа объекта
 * Загружает данные с backend (для совместимости)
 */
export const getDimensionFields = async (objectTypeId, methodology = 0) => {
  try {
    const params = await api.getElementParams(parseInt(objectTypeId), methodology);
    if (params && params.length > 0) {
      return params.map(param => ({
        id: param.id,
        label: param.name,
        type: 'text',
        typeData: param.typeData || 'string',
        required: false,
        blockId: param.blockId,
        blockName: param.blockName
      }));
    }
  } catch (error) {
    console.error('Ошибка загрузки полей размеров:', error);
  }
  
  // Fallback
  return fallbackConfig.dimensionFields[objectTypeId] || [];
};

/**
 * Получение стандартных значений для параметра из кэшированных блоков
 * @param {number} elementId - ID элемента
 * @param {string} paramId - ID параметра
 */
export const getParamStandardValues = (elementId, paramId) => {
  const cached = cachedBlocks[elementId];
  if (!cached) return [];

  for (const block of cached.blocks) {
    const param = block.params.find(p => 
      p.id === paramId || p.id === String(paramId) || String(p.id) === String(paramId)
    );
    if (param && Array.isArray(param.value)) {
      return param.value;
    }
  }
  return [];
};

/**
 * Обновить технологическую карту через PipeLine
 * @param {object} techCardData - данные в формате TechCardData
 */
export const updateTechCard = async (techCardData) => {
  try {
    return await api.updateTechCard(techCardData);
  } catch (error) {
    console.error('Ошибка обновления тех. карты:', error);
    throw error;
  }
};

/**
 * Формирует структуру TechCardData для отправки на бэкенд
 * @param {string} type - тип объекта контроля ("пластина" или "труба")
 * @param {Array} blocks - массив блоков с параметрами
 * @param {object} paramValues - значения параметров { compositeKey: value } где compositeKey = blockId.paramId
 */
export const buildTechCardPayload = (type, methodology, blocks, paramValues, selectedOptionIds = {}) => {
  const params = {};

  blocks.forEach(block => {
    params[block.id] = {
      name: block.name,
      params: {}
    };

    block.params.forEach(param => {
      // Используем составной ключ для получения значения
      const compositeKey = `${block.id}.${param.id}`;
      const value = paramValues[compositeKey];
      const selectedId = selectedOptionIds[compositeKey];
      
      params[block.id].params[param.id] = {
        name: param.name,
        val: value !== undefined && value !== '' ? value : param.value,
        options: Array.isArray(param.options) ? param.options : [],
        typeData: param.typeData || 'string',
        displayMode: param.displayMode || null
      };

      if (selectedId !== undefined && selectedId !== null && selectedId !== '') {
        params[block.id].params[param.id].selectedId = String(selectedId);
      }
    });
  });

  return {
    methodology: parseInt(methodology, 10) || 0,
    type: type,
    params: params
  };
};

const isNamedValueObject = (value) => (
  typeof value === 'object'
  && value !== null
  && !Array.isArray(value)
  && (value.name !== undefined || value.id !== undefined || value.value !== undefined)
);

const resolveExportParamValue = (param, rawValue) => {
  if (rawValue !== undefined && rawValue !== null && String(rawValue).trim() !== '') {
    return rawValue;
  }

  const fallbackValue = param?.value;

  if (fallbackValue === null || fallbackValue === undefined) {
    return '';
  }

  if (Array.isArray(fallbackValue)) {
    return '';
  }

  if (typeof fallbackValue === 'object') {
    if (fallbackValue.image || isNamedValueObject(fallbackValue)) {
      return fallbackValue;
    }
    return '';
  }

  return fallbackValue;
};

export const buildExportTechCardPayload = ({
  type,
  methodology,
  blocks,
  paramValues,
  selectedOptionIds = {},
  customFields = {},
  uploadedImages = {},
  metadata = {},
}) => {
  const params = {};

  blocks.forEach((block) => {
    params[block.id] = {
      name: block.name,
      params: {},
    };

    block.params.forEach((param) => {
      const compositeKey = `${block.id}.${param.id}`;
      const selectedId = selectedOptionIds[compositeKey];
      const exportValue = resolveExportParamValue(param, paramValues[compositeKey]);

      params[block.id].params[param.id] = {
        name: param.name,
        val: exportValue,
        displayMode: param.displayMode || null,
      };

      if (param.image) {
        params[block.id].params[param.id].image = param.image;
      }

      if (selectedId !== undefined && selectedId !== null && selectedId !== '') {
        params[block.id].params[param.id].selectedId = String(selectedId);
      }
    });
  });

  const normalizedCustomFields = Object.fromEntries(
    Object.entries(customFields)
      .map(([blockId, fields]) => [
        blockId,
        Array.isArray(fields)
          ? fields
              .filter((field) => field && ((field.name || '').trim() || (field.value || '').trim()))
              .map((field) => ({
                id: field.id,
                name: field.name || '',
                value: field.value || '',
              }))
          : [],
      ])
      .filter(([, fields]) => fields.length > 0)
  );

  const normalizedUploadedImages = Object.fromEntries(
    Object.entries(uploadedImages)
      .map(([blockId, images]) => [
        blockId,
        Array.isArray(images)
          ? images
              .filter((image) => image && image.preview)
              .map((image) => ({
                id: image.id,
                name: image.name || 'Изображение',
                preview: image.preview,
              }))
          : [],
      ])
      .filter(([, images]) => images.length > 0)
  );

  return {
    methodology: parseInt(methodology, 10) || 0,
    techCard: {
      methodology: parseInt(methodology, 10) || 0,
      type,
      params,
    },
    customFields: normalizedCustomFields,
    uploadedImages: normalizedUploadedImages,
    metadata,
  };
};

/**
 * Синхронная версия для обратной совместимости
 * Использует кэшированные данные
 */
export const getJointTypesSync = (objectTypeId) => {
  if (cachedConfig && cachedConfig.jointTypes) {
    return cachedConfig.jointTypes[objectTypeId] || [];
  }
  return fallbackConfig.jointTypes[objectTypeId] || [];
};

export const getDimensionFieldsSync = (objectTypeId) => {
  if (cachedConfig && cachedConfig.dimensionFields) {
    return cachedConfig.dimensionFields[objectTypeId] || [];
  }
  return fallbackConfig.dimensionFields[objectTypeId] || [];
};

// Экспорт для обратной совместимости
export const formConfig = fallbackConfig;

// Алиас для обратной совместимости
export const getJointTypes = getElements;
