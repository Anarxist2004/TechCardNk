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
export const getElements = async (objectTypeId) => {
  try {
    const elements = await api.getElements(parseInt(objectTypeId));
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
export const getElementData = async (elementId) => {
  try {
    const data = await api.getElementParamsWithValues(parseInt(elementId));
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
export const getDimensionFields = async (objectTypeId) => {
  try {
    const params = await api.getElementParams(parseInt(objectTypeId));
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
export const buildTechCardPayload = (type, blocks, paramValues) => {
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
      
      params[block.id].params[param.id] = {
        name: param.name,
        val: value !== undefined && value !== '' ? value : param.value
      };
    });
  });

  return {
    type: type,
    params: params
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
