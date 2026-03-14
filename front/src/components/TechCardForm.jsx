import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight, Loader2, FileCheck, CheckCircle, AlertCircle, Plus, Trash2, Image, X } from 'lucide-react';
import api from '../services/api';
import { buildTechCardPayload, updateTechCard } from '../data/formConfig';

// Компонент поля с возможностью ввода И выбора из списка
const ComboBoxField = ({ label, value, inputValue, options, onChange,
  onInputChange, loading, placeholder, disabled }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleInputChange = (e) => {
    const newValue = e.target.value;
    onInputChange(newValue);
  };

  const handleSelectOption = (option) => {
    onChange(option);
    setIsOpen(false);
  };

  // Фильтруем опции по введённому тексту
  const filteredOptions = options.filter(opt =>
    opt.name.toLowerCase().includes((inputValue || '').toLowerCase())
  );

  return (
    <div className="relative">
      <label className="block text-[#646C89] text-sm font-medium mb-2">
        {label}
      </label>
      <div className="relative">
        <input
          type="text"
          value={inputValue || ''}
          onChange={handleInputChange}
          onFocus={() => !disabled && !loading && setIsOpen(true)}
          placeholder={loading ? 'Загрузка...' : placeholder}
          disabled={disabled || loading}
          className={`
            w-full bg-[#0C1515] border border-[#646C89]
            rounded-lg px-4 py-3 pr-10
            text-white placeholder-[#646C89]
            focus:outline-none focus:border-[#0084FF]
            transition-colors
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        />
        {loading ? (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <Loader2 size={18} className="animate-spin text-[#646C89]" />
          </div>
        ) : (
          <button
            type="button"
            onClick={() => !disabled && setIsOpen(!isOpen)}
            disabled={disabled}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-[#646C89] hover:text-[#0084FF]"
          >
            <ChevronDown size={18} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </button>
        )}
      </div>

      {isOpen && !disabled && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute top-full left-0 right-0 mt-1 bg-[#0C1515] border border-[#646C89] rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
            {filteredOptions.length > 0 ? (
              filteredOptions.map(option => (
                <button
                  key={option.id}
                  type="button"
                  onClick={() => handleSelectOption(option)}
                  className={`
                    w-full text-left px-4 py-3
                    hover:bg-[#0084FF]/20 transition-colors
                    ${value === option.id ? 'bg-[#0084FF]/10 text-[#0084FF]' : 'text-white'}
                  `}
                >
                  {option.name}
                </button>
              ))
            ) : (
              <div className="px-4 py-3 text-[#646C89] text-sm">
                {inputValue ? `Будет использовано: "${inputValue}"` : 'Нет доступных вариантов'}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

// Функция валидации значения по типу данных
const validateByType = (value, typeData) => {
  if (!value || value.trim() === '') {
    return { isValid: true, error: null }; // Пустое значение допустимо
  }

  const trimmedValue = value.trim();
  const normalizedType = (typeData || 'string').toLowerCase();

  switch (normalizedType) {
    case 'int':
    case 'integer':
      // Целое число: только цифры и опциональный минус в начале
      if (!/^-?\d+$/.test(trimmedValue)) {
        return { isValid: false, error: 'Введите целое число' };
      }
      return { isValid: true, error: null };

    case 'double':
    case 'float':
    case 'real':
      // Вещественное число: цифры, опциональная точка/запятая, опциональный минус
      const normalizedNum = trimmedValue.replace(',', '.');
      if (!/^-?\d*\.?\d+$/.test(normalizedNum) || isNaN(parseFloat(normalizedNum))) {
        return { isValid: false, error: 'Введите число (например: 12.5)' };
      }
      return { isValid: true, error: null };

    case 'bool':
    case 'boolean':
      // Булево: true/false, да/нет, 1/0
      const boolValues = ['true', 'false', 'да', 'нет', '1', '0', 'yes', 'no'];
      if (!boolValues.includes(trimmedValue.toLowerCase())) {
        return { isValid: false, error: 'Введите: да/нет, true/false или 1/0' };
      }
      return { isValid: true, error: null };

    case 'string':
    case 'text':
    default:
      // Строка: любое значение допустимо
      return { isValid: true, error: null };
  }
};

// Получение типа input на основе typeData
const getInputType = (typeData) => {
  const normalizedType = (typeData || 'string').toLowerCase();
  switch (normalizedType) {
    case 'int':
    case 'integer':
    case 'double':
    case 'float':
    case 'real':
      return 'text'; // Используем text для лучшего контроля валидации
    default:
      return 'text';
  }
};

// Получение подсказки по типу данных
const getTypeHint = (typeData) => {
  const normalizedType = (typeData || 'string').toLowerCase();
  switch (normalizedType) {
    case 'int':
    case 'integer':
      return 'Целое число';
    case 'double':
    case 'float':
    case 'real':
      return 'Число';
    case 'bool':
    case 'boolean':
      return 'Да/Нет';
    default:
      return null;
  }
};

// Компонент строки таблицы с полем ввода
const TableRowInput = ({ paramKey, paramName, value, onChange, standardValues, typeData }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [touched, setTouched] = useState(false);
  const textareaRef = React.useRef(null);

  const validation = validateByType(value, typeData);
  const showError = touched && !validation.isValid;
  const typeHint = getTypeHint(typeData);

  // Автоматическое подгонка textarea по высоте текста
  const adjustHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = '0px';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  };

  useEffect(() => {
    adjustHeight();
  }, [value]);

  // Подгонка при первом рендере
  useEffect(() => {
    adjustHeight();
  }, []);

  const handleChange = (newValue) => {
    const normalizedType = (typeData || 'string').toLowerCase();

    if (normalizedType === 'int' || normalizedType === 'integer') {
      if (newValue !== '' && !/^-?\d*$/.test(newValue)) {
        return;
      }
    } else if (['double', 'float', 'real'].includes(normalizedType)) {
      if (newValue !== '' && !/^-?\d*[.,]?\d*$/.test(newValue)) {
        return;
      }
    }

    onChange(newValue);
  };

  const handleBlur = () => {
    setTouched(true);
  };

  return (
    <tr className="border-b border-[#646C89]/20 hover:bg-[#646C89]/10">
      <td className="py-2 px-2 text-white text-sm align-top" style={{ width: '300px', minWidth: '300px', maxWidth: '300px' }}>
        <span className="text-[#0084FF] font-mono mr-2">{paramKey}</span>
        {paramName}
        {typeHint && <span className="ml-1 text-xs text-[#646C89]">({typeHint})</span>}
      </td>
      <td className="py-2 px-2 relative align-top" style={{ width: '400px', minWidth: '400px' }}>
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => handleChange(e.target.value)}
            onBlur={handleBlur}
            placeholder="Введите значение"
            rows={1}
            className={`
              w-full bg-[#0C1515] border
              rounded px-3 py-1.5 pr-8
              text-white placeholder-[#646C89]
              focus:outline-none
              transition-colors text-sm
              resize-none
              ${showError
                ? 'border-red-500 focus:border-red-500'
                : 'border-[#646C89]/50 focus:border-[#0084FF]'
              }
            `}
            style={{ height: 'auto', minHeight: '28px', overflow: 'hidden', lineHeight: '1.4' }}
          />
          {standardValues && standardValues.length > 0 && (
            <button
              type="button"
              onClick={() => setIsOpen(!isOpen)}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-[#646C89] hover:text-[#0084FF]"
            >
              <ChevronDown size={16} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>
          )}
        </div>
        
        {showError && (
          <span className="text-xs text-red-500 mt-0.5 block">{validation.error}</span>
        )}

        {isOpen && standardValues && standardValues.length > 0 && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
            <div className="absolute top-full right-0 w-56 mt-1 bg-[#0C1515] border border-[#646C89] rounded-lg shadow-lg z-50 max-h-40 overflow-y-auto">
              <div className="p-2 border-b border-[#646C89]/30">
                <span className="text-xs text-[#646C89]">Стандартные значения:</span>
              </div>
              {standardValues.map((val, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    onChange(val.toString());
                    setIsOpen(false);
                    setTouched(true);
                  }}
                  className="w-full text-left px-3 py-1.5 text-white text-sm hover:bg-[#0084FF]/20 transition-colors"
                >
                  {val}
                </button>
              ))}
            </div>
          </>
        )}
      </td>
    </tr>
  );
};

// Компонент поля ввода с выпадающим списком стандартных значений и валидацией
// Отображение в одну строку: {ключ} {название} {поле ввода}
const InputWithSuggestions = ({ label, value, onChange, standardValues, loading, placeholder, typeData }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [touched, setTouched] = useState(false);

  const validation = validateByType(value, typeData);
  const showError = touched && !validation.isValid;
  const typeHint = getTypeHint(typeData);

  const handleChange = (newValue) => {
    // Для числовых типов разрешаем ввод только допустимых символов
    const normalizedType = (typeData || 'string').toLowerCase();

    if (normalizedType === 'int' || normalizedType === 'integer') {
      // Разрешаем только цифры и минус
      if (newValue !== '' && !/^-?\d*$/.test(newValue)) {
        return; // Игнорируем недопустимый ввод
      }
    } else if (['double', 'float', 'real'].includes(normalizedType)) {
      // Разрешаем цифры, точку, запятую и минус
      if (newValue !== '' && !/^-?\d*[.,]?\d*$/.test(newValue)) {
        return; // Игнорируем недопустимый ввод
      }
    }

    onChange(newValue);
  };

  const handleBlur = () => {
    setTouched(true);
  };

  return (
    <div className="relative">
      {/* Одна строка: label + input */}
      <div className="flex items-center gap-4">
        <label className="text-[#646C89] text-sm font-medium whitespace-nowrap flex-shrink-0">
          {label}
          {typeHint && (
            <span className="ml-1 text-xs text-[#646C89]/70">({typeHint})</span>
          )}
        </label>
        <div className="relative flex-1">
          <input
            type={getInputType(typeData)}
            value={value}
            onChange={(e) => handleChange(e.target.value)}
            onBlur={handleBlur}
            placeholder={placeholder}
            className={`
              w-full bg-[#0C1515] border
              rounded-lg px-4 py-2 pr-10
              text-white placeholder-[#646C89]
              focus:outline-none
              transition-colors
              ${showError
                ? 'border-red-500 focus:border-red-500'
                : 'border-[#646C89] focus:border-[#0084FF]'
              }
            `}
          />
          {loading ? (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <Loader2 size={18} className="animate-spin text-[#646C89]" />
            </div>
          ) : standardValues && standardValues.length > 0 ? (
            <button
              type="button"
              onClick={() => setIsOpen(!isOpen)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#646C89] hover:text-[#0084FF]"
            >
              <ChevronDown size={18} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>
          ) : null}
        </div>
      </div>

      {/* Сообщение об ошибке */}
      {showError && (
        <span className="text-xs text-red-500 mt-1 block pl-4">
          {validation.error}
        </span>
      )}

      {isOpen && standardValues && standardValues.length > 0 && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute top-full right-0 w-64 mt-1 bg-[#0C1515] border border-[#646C89] rounded-lg shadow-lg z-50 max-h-48 overflow-y-auto">
            <div className="p-2 border-b border-[#646C89]/30">
              <span className="text-xs text-[#646C89]">Стандартные значения:</span>
            </div>
            {standardValues.map((val, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  onChange(val.toString());
                  setIsOpen(false);
                  setTouched(true);
                }}
                className="w-full text-left px-4 py-2 text-white hover:bg-[#0084FF]/20 transition-colors"
              >
                {val}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
};


// Основной компонент формы технологической карты
const TechCardForm = () => {
  // Типы объектов
  const [objectTypes, setObjectTypes] = useState([]);
  const [loadingObjects, setLoadingObjects] = useState(true);
  const [selectedObject, setSelectedObject] = useState(null);
  const [objectInputValue, setObjectInputValue] = useState('');

  // Элементы (объекты контроля)
  const [elements, setElements] = useState([]);
  const [loadingElements, setLoadingElements] = useState(false);
  const [selectedElement, setSelectedElement] = useState(null);
  const [elementInputValue, setElementInputValue] = useState('');

  // Блоки с параметрами (новая структура)
  const [blocks, setBlocks] = useState([]);
  const [loadingBlocks, setLoadingBlocks] = useState(false);
  const [objectType, setObjectType] = useState(null); // "пластина" или "труба"

  // Значения параметров { paramId: value }
  const [paramValues, setParamValues] = useState({});

  // Поля, которые пользователь редактировал вручную (не перезаписываются бэкендом)
  const [userEditedFields, setUserEditedFields] = useState({});

  // Флаг отправки на обработку
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Состояние свёрнутых/развёрнутых блоков { blockId: true/false }
  const [collapsedBlocks, setCollapsedBlocks] = useState({});

  // Дополнительные пользовательские поля { blockId: [{id, name, value}, ...] }
  const [customFields, setCustomFields] = useState({});
  const [nextCustomFieldId, setNextCustomFieldId] = useState(1);

  // Добавление пользовательского поля в блок
  const addCustomField = (blockId) => {
    setCustomFields(prev => ({
      ...prev,
      [blockId]: [
        ...(prev[blockId] || []),
        { id: `custom_${nextCustomFieldId}`, name: '', value: '' }
      ]
    }));
    setNextCustomFieldId(prev => prev + 1);
  };

  // Обновление пользовательского поля
  const updateCustomField = (blockId, fieldId, field, value) => {
    setCustomFields(prev => ({
      ...prev,
      [blockId]: (prev[blockId] || []).map(f => 
        f.id === fieldId ? { ...f, [field]: value } : f
      )
    }));
  };

  // Удаление пользовательского поля
  const deleteCustomField = (blockId, fieldId) => {
    setCustomFields(prev => ({
      ...prev,
      [blockId]: (prev[blockId] || []).filter(f => f.id !== fieldId)
    }));
  };

  // Загруженные изображения { blockId: [{id, file, preview, name}, ...] }
  const [uploadedImages, setUploadedImages] = useState({});
  const [nextImageId, setNextImageId] = useState(1);

  // Обработчик загрузки изображения
  const handleImageUpload = (blockId, event) => {
    const files = Array.from(event.target.files);
    
    files.forEach(file => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          setUploadedImages(prev => ({
            ...prev,
            [blockId]: [
              ...(prev[blockId] || []),
              {
                id: `img_${nextImageId}`,
                file: file,
                preview: e.target.result,
                name: file.name
              }
            ]
          }));
          setNextImageId(prev => prev + 1);
        };
        reader.readAsDataURL(file);
      }
    });
    
    // Сбрасываем input для возможности повторной загрузки того же файла
    event.target.value = '';
  };

  // Удаление изображения
  const deleteImage = (blockId, imageId) => {
    setUploadedImages(prev => ({
      ...prev,
      [blockId]: (prev[blockId] || []).filter(img => img.id !== imageId)
    }));
  };

  // Функция переключения сворачивания блока
  const toggleBlockCollapse = (blockId) => {
    setCollapsedBlocks(prev => ({
      ...prev,
      [blockId]: !prev[blockId]
    }));
  };

  // Проверка, все ли параметры блока заполнены
  const isBlockComplete = (block) => {
    if (!block.params || block.params.length === 0) return true;
    
    return block.params.every(param => {
      const compositeKey = `${block.id}.${param.id}`;
      const value = paramValues[compositeKey];
      // Считаем заполненным, если есть значение или это картинка
      return (value && value.trim() !== '') || param.image;
    });
  };

  // Подсчёт заполненных параметров в блоке
  const getBlockProgress = (block) => {
    if (!block.params || block.params.length === 0) return { filled: 0, total: 0 };
    
    const total = block.params.filter(p => !p.image).length; // Не считаем картинки
    const filled = block.params.filter(param => {
      if (param.image) return false; // Картинки не считаем
      const compositeKey = `${block.id}.${param.id}`;
      const value = paramValues[compositeKey];
      return value && value.trim() !== '';
    }).length;
    
    return { filled, total };
  };

  // Загрузка типов объектов при старте
  useEffect(() => {
    const loadObjectTypes = async () => {
      try {
        const types = await api.getObjectTypes();
        setObjectTypes(types);
      } catch (error) {
        console.error('Ошибка загрузки типов объектов:', error);
      } finally {
        setLoadingObjects(false);
      }
    };
    loadObjectTypes();
  }, []);

  // Обработчик выбора объекта из списка
  const handleObjectSelect = (option) => {
    setSelectedObject(option.id);
    setObjectInputValue(option.name);
    // Сбрасываем элемент и блоки при смене объекта
    setSelectedElement(null);
    setElementInputValue('');
    setBlocks([]);
    setParamValues({});
    setObjectType(null);
  };

  // Обработчик ввода в поле объекта
  const handleObjectInputChange = (value) => {
    setObjectInputValue(value);
    // Если ввели что-то отличное от выбранного, сбрасываем selectedObject
    const matchingOption = objectTypes.find(opt => opt.name === value);
    if (matchingOption) {
      setSelectedObject(matchingOption.id);
    } else {
      setSelectedObject(null);
    }
  };

  // Обработчик выбора элемента из списка
  const handleElementSelect = (option) => {
    setSelectedElement(option.id);
    setElementInputValue(option.name);
  };

  // Обработчик ввода в поле элемента
  const handleElementInputChange = (value) => {
    setElementInputValue(value);
    const matchingOption = elements.find(opt => opt.name === value);
    if (matchingOption) {
      setSelectedElement(matchingOption.id);
    } else {
      setSelectedElement(null);
    }
  };

  // Загрузка элементов при выборе типа объекта
  useEffect(() => {
    if (!selectedObject) {
      setElements([]);
      return;
    }

    const loadElements = async () => {
      setLoadingElements(true);
      try {
        const elems = await api.getElements(parseInt(selectedObject));
        setElements(elems);
      } catch (error) {
        console.error('Ошибка загрузки элементов:', error);
        setElements([]);
      } finally {
        setLoadingElements(false);
      }
    };
    loadElements();
  }, [selectedObject]);

  // Загрузка блоков с параметрами при выборе ЭЛЕМЕНТА (объекта контроля)
  useEffect(() => {
    if (!selectedElement) {
      setBlocks([]);
      setParamValues({});
      setObjectType(null);
      return;
    }

    const loadElementData = async () => {
      setLoadingBlocks(true);
      try {
        console.log('Загружаем параметры для элемента ID:', selectedElement, 'тип:', typeof selectedElement);
        const data = await api.getElementParamsWithValues(selectedElement);
        console.log('Данные от API:', data);
        setBlocks(data.blocks || []);
        setObjectType(data.type);

        // Инициализируем значения параметров из загруженных данных
        // Используем составной ключ blockId.paramId для уникальности
        const initialValues = {};
        (data.blocks || []).forEach(block => {
          block.params.forEach(param => {
            const compositeKey = `${block.id}.${param.id}`;
            const val = param.value;
            
            // Пустое или null значение
            if (val === null || val === undefined) {
              initialValues[compositeKey] = '';
              return;
            }
            
            // Массив стандартных значений - оставляем пустым (выбор будет из подсказок)
            if (Array.isArray(val)) {
              initialValues[compositeKey] = '';
              return;
            }
            
            // Объект с id и name (например для объекта контроля)
            if (typeof val === 'object' && val !== null) {
              if (val.name !== undefined) {
                initialValues[compositeKey] = String(val.name);
              } else if (val.id !== undefined) {
                initialValues[compositeKey] = String(val.id);
              } else {
                // Это словарь { "1": "значение1", ... } - оставляем пустым для выбора
                initialValues[compositeKey] = '';
              }
              return;
            }
            
            // Простое значение (строка, число)
            initialValues[compositeKey] = String(val);
          });
        });
        setParamValues(initialValues);
      } catch (error) {
        console.error('Ошибка загрузки данных элемента:', error);
        setBlocks([]);
        setParamValues({});
      } finally {
        setLoadingBlocks(false);
      }
    };
    loadElementData();
  }, [selectedElement]);

  // Обработчик изменения значения параметра
  const handleParamChange = async (compositeKey, value) => {
    // Обновляем локальное состояние
    const updatedValues = {
      ...paramValues,
      [compositeKey]: value
    };
    setParamValues(updatedValues);

    // Помечаем поле как отредактированное пользователем
    setUserEditedFields(prev => ({
      ...prev,
      [compositeKey]: true
    }));

    // Отправляем обновлённые данные на бэкенд
    try {
      // Формируем payload для бэкенда
      const techCardPayload = buildTechCardPayload(objectType, blocks, updatedValues);
      
      console.log('Отправка изменения на бэкенд:', compositeKey, '=', value);
      console.log('Payload:', JSON.stringify(techCardPayload, null, 2));
      
      // Отправляем запрос updateTechCard
      const result = await updateTechCard(techCardPayload);
      
      console.log('Ответ от бэкенда:', result);
      
      // Если бэкенд вернул обновлённые блоки, обновляем их
      if (result.blocks && result.blocks.length > 0) {
        setBlocks(result.blocks);
        
        // Обновляем кэш стандартных значений из ответа бэкенда
        const newCache = { ...standardValuesCache };
        result.blocks.forEach(block => {
          block.params.forEach(param => {
            const key = `${block.id}.${param.id}`;
            const val = param.value;
            
            // Обновляем кэш если пришли новые стандартные значения
            if (Array.isArray(val) && val.length > 0) {
              newCache[key] = val.map(v => {
                if (typeof v === 'object' && v !== null && v.name !== undefined) {
                  return String(v.name);
                }
                return String(v);
              });
            } else if (typeof val === 'object' && val !== null && !Array.isArray(val)) {
              // Проверяем, не является ли это объектом с id/name (выбранное значение)
              if (!(val.id !== undefined && val.name !== undefined)) {
                // Это словарь вариантов
                newCache[key] = Object.values(val).map(v => String(v));
              }
            }
          });
        });
        setStandardValuesCache(newCache);
        
        // Обновляем значения параметров
        const newValues = { ...updatedValues };
        result.blocks.forEach(block => {
          block.params.forEach(param => {
            const key = `${block.id}.${param.id}`;
            
            // Если пользователь редактировал это поле — не перезаписываем
            if (userEditedFields[key]) {
              return;
            }
            
            // Получаем значение от бэкенда
            let backendValue = null;
            if (param.value !== null && !Array.isArray(param.value) && typeof param.value !== 'object') {
              backendValue = String(param.value);
            } else if (param.value && typeof param.value === 'object' && param.value.name) {
              backendValue = param.value.name;
            }
            
            // Если бэкенд прислал конкретное значение (не массив/словарь опций)
            if (backendValue !== null) {
              newValues[key] = backendValue;
            } else if (!(key in updatedValues)) {
              // Новый параметр, которого не было — оставляем пустым
              newValues[key] = '';
            }
          });
        });
        setParamValues(newValues);
      }
    } catch (error) {
      console.error('Ошибка при обновлении параметра:', error);
    }
  };

  // Кэш стандартных значений для параметров (сохраняем при первой загрузке)
  const [standardValuesCache, setStandardValuesCache] = useState({});

  // Сохраняем стандартные значения при загрузке блоков
  useEffect(() => {
    if (blocks.length > 0) {
      const cache = { ...standardValuesCache };
      blocks.forEach(block => {
        block.params.forEach(param => {
          const compositeKey = `${block.id}.${param.id}`;
          const val = param.value;
          
          // Сохраняем только если это массив или словарь (стандартные значения)
          if (Array.isArray(val) && val.length > 0) {
            cache[compositeKey] = val.map(v => {
              if (typeof v === 'object' && v !== null && v.name !== undefined) {
                return String(v.name);
              }
              return String(v);
            });
          } else if (typeof val === 'object' && val !== null && !Array.isArray(val)) {
            // Проверяем, не является ли это объектом с id/name (выбранное значение)
            if (!(val.id !== undefined && val.name !== undefined)) {
              // Это словарь вариантов
              cache[compositeKey] = Object.values(val).map(v => String(v));
            }
          }
        });
      });
      setStandardValuesCache(cache);
    }
  }, [blocks]);

  // Получение стандартных значений для параметра (из кэша или из param.value)
  const getStandardValuesForParam = (param, blockId) => {
    const compositeKey = `${blockId}.${param.id}`;
    
    // Сначала проверяем кэш
    if (standardValuesCache[compositeKey] && standardValuesCache[compositeKey].length > 0) {
      return standardValuesCache[compositeKey];
    }
    
    const val = param.value;
    
    // Если value - массив, это стандартные значения
    if (Array.isArray(val)) {
      return val.map(v => {
        // Если элемент массива - объект с name, возвращаем name
        if (typeof v === 'object' && v !== null && v.name !== undefined) {
          return String(v.name);
        }
        return String(v);
      });
    }
    
    // Если value - объект-словарь { "1": "value1", "2": "value2" }, возвращаем значения
    if (typeof val === 'object' && val !== null && !Array.isArray(val)) {
      // Проверяем, не является ли это объектом с id/name (выбранное значение)
      if (val.id !== undefined && val.name !== undefined) {
        return []; // Это выбранное значение, не список
      }
      // Это словарь вариантов - возвращаем значения
      return Object.values(val).map(v => String(v));
    }
    
    return [];
  };


  // Определяем тип данных параметра по значению
  const getParamTypeData = (param) => {
    if (Array.isArray(param.value) && param.value.length > 0) {
      const firstVal = param.value[0];
      if (typeof firstVal === 'number') {
        return Number.isInteger(firstVal) ? 'int' : 'double';
      }
      if (typeof firstVal === 'boolean') return 'bool';
    }
    if (typeof param.value === 'number') {
      return Number.isInteger(param.value) ? 'int' : 'double';
    }
    if (typeof param.value === 'boolean') return 'bool';
    return 'string';
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      // Формируем payload для бэкенда
      const techCardPayload = buildTechCardPayload(objectType, blocks, paramValues);

      console.log('═══════════════════════════════════════════════════');
      console.log('        ОТПРАВКА НА БЭКЕНД');
      console.log('═══════════════════════════════════════════════════');
      console.log(JSON.stringify(techCardPayload, null, 2));

      // Отправляем на бэкенд для обработки через PipeLine
      const result = await updateTechCard(techCardPayload);

      console.log('═══════════════════════════════════════════════════');
      console.log('        РЕЗУЛЬТАТ ОБРАБОТКИ');
      console.log('═══════════════════════════════════════════════════');
      console.log(JSON.stringify(result, null, 2));
      console.log('═══════════════════════════════════════════════════');

      // Обновляем блоки с результатом от PipeLine
      if (result.blocks && result.blocks.length > 0) {
        setBlocks(result.blocks);
        
        // Обновляем значения параметров с составным ключом
        const newValues = {};
        result.blocks.forEach(block => {
          block.params.forEach(param => {
            const compositeKey = `${block.id}.${param.id}`;
            if (param.value !== null && !Array.isArray(param.value) && typeof param.value !== 'object') {
              newValues[compositeKey] = String(param.value);
            } else if (param.value && typeof param.value === 'object' && param.value.name) {
              newValues[compositeKey] = param.value.name;
            } else {
              newValues[compositeKey] = paramValues[compositeKey] || '';
            }
          });
        });
        setParamValues(newValues);
      }

      alert('Карта успешно обработана!');
    } catch (error) {
      console.error('Ошибка обработки карты:', error);
      alert('Ошибка при обработке карты: ' + error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isFormValid = () => {
    const hasObject = objectInputValue.trim();
    const hasElement = elementInputValue.trim();

    // Проверяем валидацию всех полей в блоках
    let allParamsValid = true;
    blocks.forEach(block => {
      block.params.forEach(param => {
        const compositeKey = `${block.id}.${param.id}`;
        const value = paramValues[compositeKey] || '';
        const typeData = getParamTypeData(param);
        const validation = validateByType(value, typeData);
        if (!validation.isValid) {
          allParamsValid = false;
        }
      });
    });

    return hasObject && hasElement && allParamsValid;
  };

  const hasSelectedObject = objectInputValue.trim();
  const hasSelectedElement = selectedElement && blocks.length > 0;

  return (
    <div className="bg-[#21262F] rounded-2xl p-6 md:p-8">
      <h2 className="text-2xl font-bold text-white mb-6 pb-4 border-b border-[#646C89]/30">
        Технологическая карта
      </h2>

      <div className="space-y-6">
        {/* До выбора элемента: показываем секции выбора */}
        {!hasSelectedElement && (
          <>
            {/* Секция 1: Выбор объекта */}
            <div className="bg-[#0C1515]/50 rounded-xl p-5">
              <h3 className="text-[#0084FF] font-semibold mb-4">1. Объект контроля</h3>
              <ComboBoxField
                label="Тип объекта"
                value={selectedObject}
                inputValue={objectInputValue}
                options={objectTypes}
                onChange={handleObjectSelect}
                onInputChange={handleObjectInputChange}
                loading={loadingObjects}
                placeholder="Выберите или введите тип объекта"
              />
            </div>

            {/* Секция 2: Выбор элемента */}
            <div className={`bg-[#0C1515]/50 rounded-xl p-5 transition-opacity ${hasSelectedObject ? 'opacity-100' : 'opacity-50'}`}>
              <h3 className="text-[#FFFB78] font-semibold mb-4">2. Элемент контроля</h3>
              <ComboBoxField
                label="Тип элемента"
                value={selectedElement}
                inputValue={elementInputValue}
                options={elements}
                onChange={handleElementSelect}
                onInputChange={handleElementInputChange}
                loading={loadingElements}
                placeholder={selectedObject ? "Выберите или введите элемент" : "Введите элемент контроля"}
                disabled={!hasSelectedObject}
              />
            </div>

            {/* Индикатор загрузки */}
            {loadingBlocks && (
              <div className="bg-[#0C1515]/50 rounded-xl p-5">
                <div className="flex items-center justify-center py-8">
                  <Loader2 size={32} className="animate-spin text-[#0084FF]" />
                  <span className="ml-3 text-[#646C89]">Загрузка параметров...</span>
                </div>
              </div>
            )}

            {/* Подсказка */}
            {!loadingBlocks && !selectedElement && (
              <div className={`bg-[#0C1515]/50 rounded-xl p-5 transition-opacity ${hasSelectedObject ? 'opacity-100' : 'opacity-50'}`}>
                <h3 className="text-[#0084FF] font-semibold mb-4">3. Параметры</h3>
                <p className="text-[#646C89] text-center py-4">
                  {hasSelectedObject ? 'Выберите элемент контроля для загрузки параметров' : 'Сначала выберите тип объекта'}
                </p>
              </div>
            )}
          </>
        )}

        {/* После выбора элемента: показываем ВСЕ блоки от бэкенда (включая Объект контроля) */}
        {hasSelectedElement && (
          <>
            {/* Кнопка для возврата к выбору */}
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-[#646C89]">
                Выбрано: <span className="text-white">{objectInputValue}</span> → <span className="text-white">{elementInputValue}</span>
              </div>
              <button
                type="button"
                onClick={() => {
                  setSelectedElement(null);
                  setElementInputValue('');
                  setBlocks([]);
                  setParamValues({});
                }}
                className="text-[#0084FF] hover:text-[#0084FF]/80 text-sm transition-colors"
              >
                ← Изменить выбор
              </button>
            </div>

            {/* Все динамические блоки от бэкенда */}
            {blocks.map((block, blockIndex) => {
              const isCollapsed = collapsedBlocks[block.id];
              const isComplete = isBlockComplete(block);
              const progress = getBlockProgress(block);
              
              return (
              <div key={block.id} className="bg-[#0C1515]/50 rounded-xl p-5">
                {/* Заголовок блока с кнопкой сворачивания */}
                <div 
                  className="flex items-center justify-between cursor-pointer select-none"
                  onClick={() => toggleBlockCollapse(block.id)}
                >
                  <div className="flex items-center gap-3">
                    {/* Иконка сворачивания */}
                    <span className="text-[#646C89] transition-transform">
                      {isCollapsed ? <ChevronRight size={20} /> : <ChevronDown size={20} />}
                    </span>
                    
                    {/* Заголовок */}
                    <h3 className={`font-semibold ${blockIndex % 2 === 0 ? 'text-[#0084FF]' : 'text-[#FFFB78]'}`}>
                      {blockIndex + 1}. {block.name}
                    </h3>
                  </div>
                  
                  {/* Индикатор заполненности */}
                  <div className="flex items-center gap-2">
                    {progress.total > 0 && (
                      <span className="text-xs text-[#646C89]">
                        {progress.filled}/{progress.total}
                      </span>
                    )}
                    {isComplete ? (
                      <CheckCircle size={20} className="text-green-500" />
                    ) : (
                      <AlertCircle size={20} className="text-orange-400" />
                    )}
                  </div>
                </div>
                
                {/* Содержимое блока (скрывается при сворачивании) */}
                {!isCollapsed && (
                  <div className="mt-4">
                    {block.params.length > 0 ? (
                      <div className="overflow-x-auto">
                        <table className="w-full border-collapse table-auto">
                          <thead>
                            <tr className="border-b border-[#646C89]/30">
                              <th className="text-left text-[#646C89] text-xs font-medium py-2 px-2 whitespace-nowrap">Параметр</th>
                              <th className="text-left text-[#646C89] text-xs font-medium py-2 px-2">Значение</th>
                            </tr>
                          </thead>
                          <tbody>
                            {block.params.map(param => {
                              const compositeKey = `${block.id}.${param.id}`;
                              
                              // Если параметр содержит изображение
                              if (param.image || (param.value && typeof param.value === 'object' && param.value.image)) {
                                let imageSrc = param.image || param.value.image;
                                
                                // Если это base64 без префикса data:image, добавляем его
                                if (imageSrc && !imageSrc.startsWith('data:') && !imageSrc.startsWith('http')) {
                                  // Определяем тип изображения (по умолчанию png)
                                  imageSrc = `data:image/png;base64,${imageSrc}`;
                                }
                                
                                return (
                                  <tr key={compositeKey} className="border-b border-[#646C89]/20">
                                    <td colSpan={2} className="py-4 px-2">
                                      <div className="text-white text-sm mb-2">
                                        <span className="text-[#0084FF] font-mono mr-2">{compositeKey}</span>
                                        {param.name}
                                      </div>
                                      <div className="flex justify-center">
                                        <img 
                                          src={imageSrc} 
                                          alt={param.name}
                                          className="max-w-full max-h-96 rounded-lg border border-[#646C89]/30"
                                        />
                                      </div>
                                    </td>
                                  </tr>
                                );
                              }
                              
                              return (
                                <TableRowInput
                                  key={compositeKey}
                                  paramKey={compositeKey}
                                  paramName={param.name}
                                  value={paramValues[compositeKey] || ''}
                                  onChange={(val) => handleParamChange(compositeKey, val)}
                                  standardValues={getStandardValuesForParam(param, block.id)}
                                  typeData={getParamTypeData(param)}
                                />
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <p className="text-[#646C89] text-center py-4">Нет параметров в этом блоке</p>
                    )}

                    {/* Пользовательские дополнительные поля */}
                    {(customFields[block.id] || []).length > 0 && (
                      <div className="mt-4 border-t border-[#646C89]/30 pt-4">
                        <p className="text-xs text-[#646C89] mb-2">Дополнительные поля:</p>
                        <div className="space-y-2">
                          {customFields[block.id].map(field => (
                            <div key={field.id} className="flex gap-2 items-start">
                              <input
                                type="text"
                                value={field.name}
                                onChange={(e) => updateCustomField(block.id, field.id, 'name', e.target.value)}
                                placeholder="Название поля"
                                className="flex-1 bg-[#0C1515] border border-[#646C89]/50 rounded px-3 py-1.5 text-white text-sm placeholder-[#646C89] focus:outline-none focus:border-[#0084FF]"
                              />
                              <input
                                type="text"
                                value={field.value}
                                onChange={(e) => updateCustomField(block.id, field.id, 'value', e.target.value)}
                                placeholder="Значение"
                                className="flex-1 bg-[#0C1515] border border-[#646C89]/50 rounded px-3 py-1.5 text-white text-sm placeholder-[#646C89] focus:outline-none focus:border-[#0084FF]"
                              />
                              <button
                                type="button"
                                onClick={() => deleteCustomField(block.id, field.id)}
                                className="p-1.5 text-[#646C89] hover:text-red-500 hover:bg-red-500/10 rounded transition-colors"
                                title="Удалить поле"
                              >
                                <Trash2 size={16} />
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Загруженные пользователем изображения */}
                    {(uploadedImages[block.id] || []).length > 0 && (
                      <div className="mt-4 border-t border-[#646C89]/30 pt-4">
                        <p className="text-xs text-[#646C89] mb-2">Загруженные изображения:</p>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                          {uploadedImages[block.id].map(img => (
                            <div key={img.id} className="relative group">
                              <img
                                src={img.preview}
                                alt={img.name}
                                className="w-full h-32 object-cover rounded-lg border border-[#646C89]/30"
                              />
                              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                                <button
                                  type="button"
                                  onClick={() => deleteImage(block.id, img.id)}
                                  className="p-2 bg-red-500 hover:bg-red-600 rounded-full text-white transition-colors"
                                  title="Удалить изображение"
                                >
                                  <X size={16} />
                                </button>
                              </div>
                              <p className="text-xs text-[#646C89] mt-1 truncate" title={img.name}>
                                {img.name}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Кнопки добавления поля и изображения */}
                    <div className="mt-4 flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          addCustomField(block.id);
                        }}
                        className="flex items-center gap-2 px-3 py-1.5 text-[#0084FF] hover:bg-[#0084FF]/10 rounded-lg transition-colors text-sm"
                      >
                        <Plus size={16} />
                        Добавить поле
                      </button>
                      
                      <label className="flex items-center gap-2 px-3 py-1.5 text-[#0084FF] hover:bg-[#0084FF]/10 rounded-lg transition-colors text-sm cursor-pointer">
                        <Image size={16} />
                        Добавить фото
                        <input
                          type="file"
                          accept="image/*"
                          multiple
                          onChange={(e) => handleImageUpload(block.id, e)}
                          className="hidden"
                        />
                      </label>
                    </div>
                  </div>
                )}
              </div>
              );
            })}
          </>
        )}


        {/* Кнопка отправки */}
        <div className="pt-4">
          <button
            onClick={handleSubmit}
            disabled={!isFormValid() || isSubmitting}
            className={`
              w-full flex items-center justify-center gap-3
              py-4 rounded-xl font-semibold text-lg
              transition-all
              ${isFormValid() && !isSubmitting
                ? 'bg-[#0084FF] hover:bg-[#0084FF]/80 text-white shadow-lg hover:shadow-[#0084FF]/20'
                : 'bg-[#646C89]/30 text-[#646C89] cursor-not-allowed'
              }
            `}
          >
            {isSubmitting ? (
              <>
                <Loader2 size={24} className="animate-spin" />
                Обработка...
              </>
            ) : (
              <>
                <FileCheck size={24} />
                Сформировать карту
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default TechCardForm;
