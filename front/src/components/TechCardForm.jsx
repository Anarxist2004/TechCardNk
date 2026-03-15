import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { ChevronDown, ChevronRight, Loader2, FileCheck, CheckCircle, AlertCircle, Plus, Trash2, Image, X } from 'lucide-react';
import api from '../services/api';
import { buildTechCardPayload, updateTechCard } from '../data/formConfig';

const ROSATOM_METHODOLOGY_ID = '0';
const GAZPROM_METHODOLOGY_ID = '1';
const DISPLAY_MODE_NUMBER_ONLY = 'number_only';
const DISPLAY_MODE_IMAGE_FULL = 'image_full';
const GAZPROM_SCHEME_PARAM_KEY = '6.1';
const DEFAULT_ACTIVE_TAB = 'overview';

const BLOCK_TAB_GROUPS = [
  {
    id: 'overview',
    label: 'Контекст',
    description: 'Объект, документация и размеры',
    blockIds: [1, 2, 3, 4],
  },
  {
    id: 'setup',
    label: 'Оснащение',
    description: 'Средства, схема и подготовка',
    blockIds: [5, 6, 7],
  },
  {
    id: 'operations',
    label: 'Контроль',
    description: 'Порядок проведения операций',
    blockIds: [8],
  },
  {
    id: 'assessment',
    label: 'Оценка',
    description: 'Расшифровка и качество',
    blockIds: [9, 10],
  },
];

const EXTRA_BLOCK_TAB = {
  id: 'other',
  label: 'Дополнительно',
  description: 'Прочие разделы техкарты',
};

const getBlockTabId = (blockId) => {
  const normalizedBlockId = Number(blockId);
  const matchedGroup = BLOCK_TAB_GROUPS.find((group) => group.blockIds.includes(normalizedBlockId));
  return matchedGroup?.id || EXTRA_BLOCK_TAB.id;
};

const buildBlockTabs = (blocks = []) => {
  const tabs = BLOCK_TAB_GROUPS
    .map((group) => ({
      ...group,
      blocks: blocks.filter((block) => group.blockIds.includes(Number(block.id))),
    }))
    .filter((group) => group.blocks.length > 0);

  const extraBlocks = blocks.filter((block) => getBlockTabId(block.id) === EXTRA_BLOCK_TAB.id);
  if (extraBlocks.length > 0) {
    tabs.push({
      ...EXTRA_BLOCK_TAB,
      blocks: extraBlocks,
    });
  }

  return tabs;
};

const normalizeSuggestionOptions = (options) => {
  if (!Array.isArray(options)) {
    return [];
  }

  return options.map((option) => {
    if (typeof option === 'object' && option !== null) {
      const label = option.name ?? option.label ?? option.value ?? '';
      return {
        id: option.id ?? null,
        label: String(label),
        value: String(label),
      };
    }

    return {
      id: null,
      label: String(option),
      value: String(option),
    };
  });
};

const normalizeOptionValues = (options) => {
  if (!Array.isArray(options)) {
    return [];
  }

  return options
    .map((option) => {
      if (typeof option === 'object' && option !== null) {
        const label = option.name ?? option.label ?? option.value ?? '';
        if (!label) {
          return null;
        }

        return {
          id: option.id ?? null,
          name: String(label),
        };
      }

      return String(option);
    })
    .filter(Boolean);
};

const isSelectedValueObject = (value) => (
  typeof value === 'object'
  && value !== null
  && !Array.isArray(value)
  && value.id !== undefined
  && value.name !== undefined
);

const getInputValueFromParam = (param, fallbackValue = '') => {
  const val = param?.value;

  if (val === null || val === undefined) {
    return fallbackValue;
  }

  if (Array.isArray(val)) {
    return fallbackValue;
  }

  if (typeof val === 'object') {
    if (val.name !== undefined) {
      return String(val.name);
    }
    if (val.id !== undefined) {
      return String(val.id);
    }
    return fallbackValue;
  }

  return String(val);
};

const getSelectedIdFromParam = (param) => {
  if (param?.selectedId !== undefined && param?.selectedId !== null && param?.selectedId !== '') {
    return String(param.selectedId);
  }

  const val = param?.value;
  if (val && typeof val === 'object' && !Array.isArray(val) && val.id !== undefined) {
    return String(val.id);
  }

  return null;
};

const resolveImageSrc = (imageSrc) => {
  if (!imageSrc) {
    return '';
  }

  const normalizedSrc = String(imageSrc).trim();

  if (
    normalizedSrc.startsWith('data:') ||
    normalizedSrc.startsWith('http://') ||
    normalizedSrc.startsWith('https://') ||
    normalizedSrc.startsWith('blob:')
  ) {
    return normalizedSrc;
  }

  if (normalizedSrc.startsWith('/')) {
    return normalizedSrc;
  }

  if (normalizedSrc.startsWith('res/')) {
    return `/${normalizedSrc}`;
  }

  const looksLikeBase64 = (
    !normalizedSrc.includes('/')
    && !normalizedSrc.includes('\\')
    && !normalizedSrc.includes(' ')
    && /^[A-Za-z0-9+/=]+$/.test(normalizedSrc)
    && normalizedSrc.length > 64
  );

  if (looksLikeBase64) {
    return `data:image/png;base64,${normalizedSrc}`;
  }

  return normalizedSrc;
};

const buildFormStateFromBlocks = (blocks = []) => {
  const values = {};
  const selectedIds = {};

  blocks.forEach((block) => {
    block.params.forEach((param) => {
      const compositeKey = `${block.id}.${param.id}`;
      values[compositeKey] = getInputValueFromParam(param, '');

      const selectedId = getSelectedIdFromParam(param);
      if (selectedId !== null) {
        selectedIds[compositeKey] = selectedId;
      }
    });
  });

  return { values, selectedIds };
};

const buildStandardValuesCacheFromBlocks = (blocks = []) => {
  const cache = {};

  blocks.forEach((block) => {
    block.params.forEach((param) => {
      const compositeKey = `${block.id}.${param.id}`;
      const optionValues = normalizeOptionValues(param.options);
      const val = param.value;

      if (optionValues.length > 0) {
        cache[compositeKey] = optionValues;
        return;
      }

      if (Array.isArray(val) && val.length > 0) {
        cache[compositeKey] = normalizeOptionValues(val);
        return;
      }

      if (typeof val === 'object' && val !== null && !Array.isArray(val) && !isSelectedValueObject(val)) {
        cache[compositeKey] = Object.values(val).map((item) => String(item));
      }
    });
  });

  return cache;
};

const getDropdownPosition = (anchorRect, preferredWidth, estimatedHeight) => {
  const viewportPadding = 8;
  const offset = 8;
  const width = Math.min(preferredWidth, window.innerWidth - viewportPadding * 2);
  const left = Math.min(
    Math.max(viewportPadding, anchorRect.right - width),
    window.innerWidth - width - viewportPadding
  );
  const spaceBelow = window.innerHeight - anchorRect.bottom - viewportPadding - offset;
  const spaceAbove = anchorRect.top - viewportPadding - offset;
  const openAbove = spaceAbove > spaceBelow && spaceAbove >= 120;

  return {
    left: `${left}px`,
    width: `${width}px`,
    maxHeight: `${Math.max(120, Math.min(estimatedHeight, openAbove ? spaceAbove : spaceBelow))}px`,
    ...(openAbove
      ? { bottom: `${window.innerHeight - anchorRect.top + offset}px` }
      : { top: `${anchorRect.bottom + offset}px` }),
  };
};

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
            focus:outline-none focus:border-[#D97B54]
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
            className="absolute right-3 top-1/2 -translate-y-1/2 text-[#646C89] hover:text-[#D97B54]"
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
                    hover:bg-[#D97B54]/20 transition-colors
                    ${value === option.id ? 'bg-[#D97B54]/10 text-[#D97B54]' : 'text-white'}
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
const TableRowInput = ({
  paramKey,
  paramName,
  value,
  onChange,
  onCreateOption,
  standardValues,
  typeData,
  displayMode,
  canCreateOption,
  isCreatingOption,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [touched, setTouched] = useState(false);
  const [dropdownStyle, setDropdownStyle] = useState(null);
  const textareaRef = React.useRef(null);
  const dropdownAnchorRef = React.useRef(null);

  const validation = validateByType(value, typeData);
  const showError = touched && !validation.isValid;
  const typeHint = getTypeHint(typeData);
  const suggestionOptions = normalizeSuggestionOptions(standardValues);
  const isNumberOnlyMode = displayMode === DISPLAY_MODE_NUMBER_ONLY;
  const trimmedValue = String(value || '').trim();
  const hasExistingOption = suggestionOptions.some((option) => {
    const optionLabel = String(option.label || option.value || '').trim().toLowerCase();
    return optionLabel === trimmedValue.toLowerCase();
  });
  const canSaveOption = Boolean(canCreateOption) && trimmedValue !== '' && !hasExistingOption;
  const hasActionButtons = suggestionOptions.length > 0 || canSaveOption || isCreatingOption;

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

  useEffect(() => {
    adjustHeight();
  }, []);

  useEffect(() => {
    if (!isOpen || suggestionOptions.length === 0) {
      setDropdownStyle(null);
      return undefined;
    }

    const updateDropdownPosition = () => {
      if (!dropdownAnchorRef.current) {
        return;
      }

      const anchorRect = dropdownAnchorRef.current.getBoundingClientRect();
      setDropdownStyle(getDropdownPosition(anchorRect, 224, 160));
    };

    updateDropdownPosition();
    window.addEventListener('resize', updateDropdownPosition);
    window.addEventListener('scroll', updateDropdownPosition, true);

    return () => {
      window.removeEventListener('resize', updateDropdownPosition);
      window.removeEventListener('scroll', updateDropdownPosition, true);
    };
  }, [isOpen, suggestionOptions.length]);

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

    onChange(newValue, null);
  };

  const handleBlur = () => {
    setTouched(true);
  };

  return (
    <tr className="border-b border-[#646C89]/20 hover:bg-[#646C89]/10">
      {!isNumberOnlyMode && (
        <td className="py-2 px-2 text-white text-sm align-top" style={{ width: '300px', minWidth: '300px', maxWidth: '300px' }}>
          <span className="text-[#D97B54] font-mono mr-2">{paramKey}</span>
          {paramName}
          {typeHint && <span className="ml-1 text-xs text-[#646C89]">({typeHint})</span>}
        </td>
      )}
      <td
        colSpan={isNumberOnlyMode ? 2 : undefined}
        className="py-2 px-2 align-top"
        style={isNumberOnlyMode ? undefined : { width: '400px', minWidth: '400px' }}
      >
        <div className={isNumberOnlyMode ? 'flex items-start gap-3 w-full' : ''}>
          {isNumberOnlyMode && (
            <span className="text-[#D97B54] font-mono text-sm shrink-0 pt-1">{paramKey}</span>
          )}
          <div ref={dropdownAnchorRef} className={isNumberOnlyMode ? 'relative flex-1 min-w-0' : 'relative'}>
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => handleChange(e.target.value)}
            onBlur={handleBlur}
            placeholder="Введите значение"
            rows={1}
            className={`
              w-full bg-[#0C1515] border
              rounded px-3 py-1.5 ${hasActionButtons ? 'pr-14' : 'pr-3'}
              text-white placeholder-[#646C89]
              focus:outline-none
              transition-colors text-sm
              resize-none
              ${showError
                ? 'border-red-500 focus:border-red-500'
                : 'border-[#646C89]/50 focus:border-[#D97B54]'
              }
            `}
            style={{ height: 'auto', minHeight: '28px', overflow: 'hidden', lineHeight: '1.4' }}
          />
          {(canSaveOption || isCreatingOption) && (
            <button
              type="button"
              onClick={() => onCreateOption?.()}
              disabled={isCreatingOption}
              className={`absolute top-1/2 -translate-y-1/2 text-[#646C89] hover:text-[#35C759] ${suggestionOptions.length > 0 ? 'right-8' : 'right-2'}`}
              title="Сохранить значение в справочник"
            >
              {isCreatingOption ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
            </button>
          )}
          {suggestionOptions.length > 0 && (
            <button
              type="button"
              onClick={() => setIsOpen(!isOpen)}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-[#646C89] hover:text-[#D97B54]"
            >
              <ChevronDown size={16} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>
          )}
        {showError && (
          <span className="text-xs text-red-500 mt-0.5 block">{validation.error}</span>
        )}

        {isOpen && suggestionOptions.length > 0 && dropdownStyle && createPortal(
          <>
            <div className="fixed inset-0 z-[90]" onClick={() => setIsOpen(false)} />
            <div
              className="fixed bg-[#0C1515] border border-[#646C89] rounded-lg shadow-lg z-[100] overflow-y-auto"
              style={dropdownStyle}
            >
              <div className="p-2 border-b border-[#646C89]/30">
                <span className="text-xs text-[#646C89]">Стандартные значения:</span>
              </div>
              {suggestionOptions.map((option, idx) => (
                <button
                  key={`${option.id ?? option.value}_${idx}`}
                  type="button"
                  onClick={() => {
                    onChange(option.value, option.id);
                    setIsOpen(false);
                    setTouched(true);
                  }}
                  className="w-full text-left px-3 py-1.5 text-white text-sm hover:bg-[#D97B54]/20 transition-colors"
                >
                  {option.label}
                </button>
              ))}
            </div>
          </>,
          document.body
        )}
          </div>
        </div>
      </td>
    </tr>
  );
};

// Компонент поля ввода с выпадающим списком стандартных значений и валидацией
// Отображение в одну строку: {ключ} {название} {поле ввода}
const InputWithSuggestions = ({ label, value, onChange, standardValues, loading, placeholder, typeData }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [touched, setTouched] = useState(false);
  const [dropdownStyle, setDropdownStyle] = useState(null);
  const dropdownAnchorRef = React.useRef(null);

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

  useEffect(() => {
    if (!isOpen || !standardValues || standardValues.length === 0) {
      setDropdownStyle(null);
      return undefined;
    }

    const updateDropdownPosition = () => {
      if (!dropdownAnchorRef.current) {
        return;
      }

      const anchorRect = dropdownAnchorRef.current.getBoundingClientRect();
      setDropdownStyle(getDropdownPosition(anchorRect, 256, 192));
    };

    updateDropdownPosition();
    window.addEventListener('resize', updateDropdownPosition);
    window.addEventListener('scroll', updateDropdownPosition, true);

    return () => {
      window.removeEventListener('resize', updateDropdownPosition);
      window.removeEventListener('scroll', updateDropdownPosition, true);
    };
  }, [isOpen, standardValues]);

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
        <div ref={dropdownAnchorRef} className="relative flex-1">
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
                : 'border-[#646C89] focus:border-[#D97B54]'
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
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#646C89] hover:text-[#D97B54]"
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

      {isOpen && standardValues && standardValues.length > 0 && dropdownStyle && createPortal(
        <>
          <div className="fixed inset-0 z-[90]" onClick={() => setIsOpen(false)} />
          <div
            className="fixed bg-[#0C1515] border border-[#646C89] rounded-lg shadow-lg z-[100] overflow-y-auto"
            style={dropdownStyle}
          >
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
                className="w-full text-left px-4 py-2 text-white hover:bg-[#D97B54]/20 transition-colors"
              >
                {val}
              </button>
            ))}
          </div>
        </>,
        document.body
      )}
    </div>
  );
};


// Основной компонент формы технологической карты
const TechCardForm = () => {
  const [methodologies, setMethodologies] = useState([]);
  const [loadingMethodologies, setLoadingMethodologies] = useState(true);
  const [selectedMethodology, setSelectedMethodology] = useState(null);
  const [methodologyInputValue, setMethodologyInputValue] = useState('');

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
  const [selectedOptionIds, setSelectedOptionIds] = useState({});

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
  const [standardValuesCache, setStandardValuesCache] = useState({});
  const [savingOptionKey, setSavingOptionKey] = useState(null);
  const [activeTabId, setActiveTabId] = useState(DEFAULT_ACTIVE_TAB);

  const isRosatomMethodology = selectedMethodology === ROSATOM_METHODOLOGY_ID;
  const isGazpromMethodology = selectedMethodology === GAZPROM_METHODOLOGY_ID;

  const resetLoadedTechCard = () => {
    setSelectedElement(null);
    setElementInputValue('');
    setBlocks([]);
    setParamValues({});
    setSelectedOptionIds({});
    setObjectType(null);
    setUserEditedFields({});
    setCollapsedBlocks({});
    setCustomFields({});
    setUploadedImages({});
    setStandardValuesCache({});
    setActiveTabId(DEFAULT_ACTIVE_TAB);
  };

  const resetObjectSelection = () => {
    setSelectedObject(null);
    setObjectInputValue('');
    setElements([]);
    resetLoadedTechCard();
  };

  const resetMethodologySelection = () => {
    setSelectedMethodology(null);
    setMethodologyInputValue('');
    setObjectTypes([]);
    setLoadingObjects(false);
    resetObjectSelection();
  };

  const applyLoadedTechCard = (data) => {
    const nextBlocks = data.blocks || [];
    const { values, selectedIds } = buildFormStateFromBlocks(nextBlocks);
    const nextTabs = buildBlockTabs(nextBlocks);

    setBlocks(nextBlocks);
    setObjectType(data.type || null);
    setParamValues(values);
    setSelectedOptionIds(selectedIds);
    setStandardValuesCache(buildStandardValuesCacheFromBlocks(nextBlocks));
    setActiveTabId(nextTabs[0]?.id || DEFAULT_ACTIVE_TAB);
  };

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

  // Загрузка начальных данных при старте
  useEffect(() => {
    const loadInitialData = async () => {
      setLoadingMethodologies(true);
      try {
        const availableMethodologies = await api.getMethodologies();
        setMethodologies(availableMethodologies);
      } catch (error) {
        console.error('Ошибка загрузки начальных данных:', error);
      } finally {
        setLoadingMethodologies(false);
      }
    };
    loadInitialData();
  }, []);

  useEffect(() => {
    if (!selectedMethodology) {
      setObjectTypes([]);
      setLoadingObjects(false);
      setLoadingBlocks(false);
      return;
    }

    if (selectedMethodology === GAZPROM_METHODOLOGY_ID) {
      setObjectTypes([]);
      setElements([]);
      setLoadingObjects(false);

      const loadFullTechCard = async () => {
        setLoadingBlocks(true);
        try {
          const data = await api.getFullTechCard(selectedMethodology);
          applyLoadedTechCard(data);
        } catch (error) {
          console.error('Ошибка загрузки полной техкарты Газпром:', error);
          setBlocks([]);
          setParamValues({});
          setSelectedOptionIds({});
          setStandardValuesCache({});
          setObjectType(null);
        } finally {
          setLoadingBlocks(false);
        }
      };

      loadFullTechCard();
      return;
    }

    const loadObjectTypes = async () => {
      setLoadingObjects(true);
      try {
        const types = await api.getObjectTypes(selectedMethodology);
        setObjectTypes(types);
      } catch (error) {
        console.error('Ошибка загрузки типов объектов:', error);
        setObjectTypes([]);
      } finally {
        setLoadingObjects(false);
      }
    };

    loadObjectTypes();
  }, [selectedMethodology]);

  useEffect(() => {
    const availableTabs = buildBlockTabs(blocks);

    if (availableTabs.length === 0) {
      if (activeTabId !== DEFAULT_ACTIVE_TAB) {
        setActiveTabId(DEFAULT_ACTIVE_TAB);
      }
      return;
    }

    if (!availableTabs.some((tab) => tab.id === activeTabId)) {
      setActiveTabId(availableTabs[0].id);
    }
  }, [blocks, activeTabId]);

  const handleMethodologySelect = (option) => {
    setSelectedMethodology(option.id);
    setMethodologyInputValue(option.name);
    resetObjectSelection();
  };

  const handleMethodologyInputChange = (value) => {
    setMethodologyInputValue(value);

    const matchingOption = methodologies.find((option) => option.name === value);
    const nextMethodologyId = matchingOption ? matchingOption.id : null;

    if (nextMethodologyId !== selectedMethodology) {
      resetObjectSelection();
    }

    setSelectedMethodology(nextMethodologyId);
  };

  // Обработчик выбора объекта из списка
  const handleObjectSelect = (option) => {
    setSelectedObject(option.id);
    setObjectInputValue(option.name);
    resetLoadedTechCard();
  };

  // Обработчик ввода в поле объекта
  const handleObjectInputChange = (value) => {
    setObjectInputValue(value);
    // Если ввели что-то отличное от выбранного, сбрасываем selectedObject
    const matchingOption = objectTypes.find(opt => opt.name === value);
    if (matchingOption) {
      if (matchingOption.id !== selectedObject) {
        resetLoadedTechCard();
      }
      setSelectedObject(matchingOption.id);
    } else {
      resetLoadedTechCard();
      setElements([]);
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
    if (!selectedMethodology || !selectedObject) {
      setElements([]);
      return;
    }

    const loadElements = async () => {
      setLoadingElements(true);
      try {
        const elems = await api.getElements(parseInt(selectedObject), selectedMethodology);
        setElements(elems);
      } catch (error) {
        console.error('Ошибка загрузки элементов:', error);
        setElements([]);
      } finally {
        setLoadingElements(false);
      }
    };
    loadElements();
  }, [selectedMethodology, selectedObject]);

  // Загрузка блоков с параметрами при выборе ЭЛЕМЕНТА (объекта контроля)
  useEffect(() => {
    if (isGazpromMethodology) {
      return;
    }

    if (!selectedMethodology || !selectedElement) {
      setBlocks([]);
      setParamValues({});
      setSelectedOptionIds({});
      setStandardValuesCache({});
      setObjectType(null);
      return;
    }

    const loadElementData = async () => {
      setLoadingBlocks(true);
      try {
        console.log('Загружаем параметры для элемента ID:', selectedElement, 'тип:', typeof selectedElement);
        const data = await api.getElementParamsWithValues(selectedElement, selectedMethodology);
        console.log('Данные от API:', data);
        applyLoadedTechCard(data);
      } catch (error) {
        console.error('Ошибка загрузки данных элемента:', error);
        setBlocks([]);
        setParamValues({});
        setSelectedOptionIds({});
        setStandardValuesCache({});
      } finally {
        setLoadingBlocks(false);
      }
    };
    loadElementData();
  }, [selectedMethodology, selectedElement]);

  // Обработчик изменения значения параметра
  const handleParamChange = async (compositeKey, value, selectedOptionId = null) => {
    // Обновляем локальное состояние
    const updatedValues = {
      ...paramValues,
      [compositeKey]: value
    };
    const updatedSelectedOptionIds = { ...selectedOptionIds };

    if (selectedOptionId !== null && selectedOptionId !== undefined && selectedOptionId !== '') {
      updatedSelectedOptionIds[compositeKey] = String(selectedOptionId);
    } else {
      delete updatedSelectedOptionIds[compositeKey];
    }

    setParamValues(updatedValues);
    setSelectedOptionIds(updatedSelectedOptionIds);

    // Помечаем поле как отредактированное пользователем
    setUserEditedFields(prev => ({
      ...prev,
      [compositeKey]: true
    }));

    const shouldSyncRosatom = isRosatomMethodology;
    const shouldSyncGazpromScheme = (
      isGazpromMethodology
      && compositeKey === GAZPROM_SCHEME_PARAM_KEY
      && selectedOptionId !== null
      && selectedOptionId !== undefined
      && selectedOptionId !== ''
    );

    if (!shouldSyncRosatom && !shouldSyncGazpromScheme) {
      return;
    }

    // Отправляем обновлённые данные на бэкенд
    try {
      // Формируем payload для бэкенда
      const techCardPayload = buildTechCardPayload(
        objectType,
        selectedMethodology,
        blocks,
        updatedValues,
        updatedSelectedOptionIds
      );
      
      console.log('Отправка изменения на бэкенд:', compositeKey, '=', value);
      console.log('Payload:', JSON.stringify(techCardPayload, null, 2));
      
      // Отправляем запрос updateTechCard
      const result = await updateTechCard(techCardPayload);
      
      console.log('Ответ от бэкенда:', result);
      
      // Если бэкенд вернул обновлённые блоки, обновляем их
      if (result.blocks && result.blocks.length > 0) {
        applyLoadedTechCard(result);
        return;
        /* setBlocks(result.blocks);
        
        // Обновляем кэш стандартных значений из ответа бэкенда
        const newCache = { ...standardValuesCache };
        result.blocks.forEach(block => {
          block.params.forEach(param => {
            const key = `${block.id}.${param.id}`;
            const optionValues = normalizeOptionValues(param.options);
            const val = param.value;
            
            // Обновляем кэш если пришли новые стандартные значения
            if (optionValues.length > 0) {
              newCache[key] = optionValues;
            } else if (Array.isArray(val) && val.length > 0) {
              newCache[key] = normalizeOptionValues(val);
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
        setParamValues(newValues); */
      }
    } catch (error) {
      console.error('Ошибка при обновлении параметра:', error);
    }
  };

  // Сохраняем стандартные значения при загрузке блоков
  useEffect(() => {
    setStandardValuesCache(buildStandardValuesCacheFromBlocks(blocks));
    return;
    /* if (blocks.length > 0) {
      const cache = { ...standardValuesCache };
      blocks.forEach(block => {
        block.params.forEach(param => {
          const compositeKey = `${block.id}.${param.id}`;
          const optionValues = normalizeOptionValues(param.options);
          const val = param.value;
          
          // Сохраняем только если это массив или словарь (стандартные значения)
          if (optionValues.length > 0) {
            cache[compositeKey] = optionValues;
          } else if (Array.isArray(val) && val.length > 0) {
            cache[compositeKey] = normalizeOptionValues(val);
          } else if (typeof val === 'object' && val !== null && !Array.isArray(val)) {
            // Проверяем, не является ли это объектом с id/name (выбранное значение)
            if (!(val.id !== undefined && val.name !== undefined)) {
              // Это словарь вариантов
              cache[compositeKey] = Object.values(val).map(v => String(v));
            }
          }
        });
      });
      setStandardValuesCache(cache); */
  }, [blocks]);

  // Получение стандартных значений для параметра (из кэша или из param.value)
  const handleCreateParamOption = async (blockId, param) => {
    const compositeKey = `${blockId}.${param.id}`;
    const currentValue = String(paramValues[compositeKey] || '').trim();

    if (!currentValue) {
      return;
    }

    setSavingOptionKey(compositeKey);

    try {
      const techCardPayload = buildTechCardPayload(
        objectType,
        selectedMethodology,
        blocks,
        paramValues,
        selectedOptionIds
      );

      const result = await api.createParamOption({
        methodology: parseInt(selectedMethodology, 10) || 0,
        blockId,
        paramId: param.id,
        value: currentValue,
        techCard: techCardPayload,
      });

      if (!result?.success) {
        throw new Error(result?.message || 'Не удалось сохранить значение');
      }

      const savedName = String(result?.item?.name || currentValue);
      const savedId = result?.item?.id ?? null;
      const savedOption = savedId !== null && savedId !== undefined
        ? { id: String(savedId), name: savedName }
        : savedName;

      setParamValues((prev) => ({
        ...prev,
        [compositeKey]: savedName,
      }));

      if (savedId !== null && savedId !== undefined) {
        setSelectedOptionIds((prev) => ({
          ...prev,
          [compositeKey]: String(savedId),
        }));
      }

      setStandardValuesCache((prev) => {
        const currentOptions = (prev[compositeKey] && prev[compositeKey].length > 0)
          ? prev[compositeKey]
          : normalizeOptionValues(param.options);

        const optionExists = currentOptions.some((option) => {
          if (typeof option === 'object' && option !== null) {
            return String(option.name || '').trim().toLowerCase() === savedName.toLowerCase();
          }

          return String(option).trim().toLowerCase() === savedName.toLowerCase();
        });

        if (optionExists) {
          return prev;
        }

        return {
          ...prev,
          [compositeKey]: [...currentOptions, savedOption],
        };
      });

      if (isGazpromMethodology && compositeKey === GAZPROM_SCHEME_PARAM_KEY && savedId !== null && savedId !== undefined) {
        await handleParamChange(compositeKey, savedName, String(savedId));
      }

      alert(result.message || 'Значение сохранено');
    } catch (error) {
      console.error('Ошибка сохранения значения:', error);
      alert(`Ошибка сохранения значения: ${error.message}`);
    } finally {
      setSavingOptionKey(null);
    }
  };

  const getStandardValuesForParam = (param, blockId) => {
    const compositeKey = `${blockId}.${param.id}`;
    
    // Сначала проверяем кэш
    if (standardValuesCache[compositeKey] && standardValuesCache[compositeKey].length > 0) {
      return standardValuesCache[compositeKey];
    }

    const optionValues = normalizeOptionValues(param.options);
    if (optionValues.length > 0) {
      return optionValues;
    }
    
    const val = param.value;

    if (Array.isArray(val)) {
      return normalizeOptionValues(val);
    }

    if (typeof val === 'object' && val !== null && !Array.isArray(val) && isSelectedValueObject(val)) {
      return [];
    }
    
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
    if (param.typeData) {
      return param.typeData;
    }

    if (Array.isArray(param.options) && param.options.length > 0) {
      const firstOption = param.options[0];
      if (typeof firstOption === 'number') {
        return Number.isInteger(firstOption) ? 'int' : 'double';
      }
      if (typeof firstOption === 'boolean') return 'bool';
    }

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
      const techCardPayload = buildTechCardPayload(
        objectType,
        selectedMethodology,
        blocks,
        paramValues,
        selectedOptionIds
      );

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
        applyLoadedTechCard(result);
        alert('РљР°СЂС‚Р° СѓСЃРїРµС€РЅРѕ РѕР±СЂР°Р±РѕС‚Р°РЅР°!');
        return;
        /* setBlocks(result.blocks);
        
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
        setParamValues(newValues); */
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
    const hasMethodology = Boolean(selectedMethodology);
    const hasObject = isGazpromMethodology ? true : objectInputValue.trim();
    const hasElement = isGazpromMethodology ? blocks.length > 0 : elementInputValue.trim();

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

    return hasMethodology && hasObject && hasElement && allParamsValid;
  };

  const hasSelectedMethodology = Boolean(selectedMethodology);
  const hasSelectedObject = isGazpromMethodology ? true : objectInputValue.trim();
  const hasSelectedElement = isGazpromMethodology ? blocks.length > 0 : selectedElement && blocks.length > 0;
  const blockTabs = buildBlockTabs(blocks);
  const activeTab = blockTabs.find((tab) => tab.id === activeTabId) || blockTabs[0] || null;
  const visibleBlocks = activeTab?.blocks || blocks;

  return (
    <div className="bg-[#21262F] rounded-2xl p-6 md:p-8">
      <h2 className="text-2xl font-bold text-white mb-6 pb-4 border-b border-[#646C89]/30">
        Технологическая карта
      </h2>

      <div className="space-y-6">
        {/* До выбора элемента: показываем секции выбора */}
        {!hasSelectedElement && (
          <>
            {/* Секция 1: Выбор методики */}
            <div className="bg-[#0C1515]/50 rounded-xl p-5">
              <h3 className="text-[#D97B54] font-semibold mb-4">1. Методика</h3>
              <ComboBoxField
                label="Методика контроля"
                value={selectedMethodology}
                inputValue={methodologyInputValue}
                options={methodologies}
                onChange={handleMethodologySelect}
                onInputChange={handleMethodologyInputChange}
                loading={loadingMethodologies}
                placeholder="Выберите методику"
              />
            </div>

            {!isGazpromMethodology && (
              <>
                {/* Секция 2: Выбор объекта */}
                <div className={`bg-[#0C1515]/50 rounded-xl p-5 transition-opacity ${hasSelectedMethodology ? 'opacity-100' : 'opacity-50'}`}>
                  <h3 className="text-[#D97B54] font-semibold mb-4">2. Объект контроля</h3>
                  <ComboBoxField
                    label="Тип объекта"
                    value={selectedObject}
                    inputValue={objectInputValue}
                    options={objectTypes}
                    onChange={handleObjectSelect}
                    onInputChange={handleObjectInputChange}
                    loading={loadingObjects}
                    placeholder="Выберите или введите тип объекта"
                    disabled={!hasSelectedMethodology}
                  />
                </div>

                {/* Секция 3: Выбор элемента */}
                <div className={`bg-[#0C1515]/50 rounded-xl p-5 transition-opacity ${hasSelectedMethodology && hasSelectedObject ? 'opacity-100' : 'opacity-50'}`}>
                  <h3 className="text-[#8FB996] font-semibold mb-4">3. Элемент контроля</h3>
                  <ComboBoxField
                    label="Тип элемента"
                    value={selectedElement}
                    inputValue={elementInputValue}
                    options={elements}
                    onChange={handleElementSelect}
                    onInputChange={handleElementInputChange}
                    loading={loadingElements}
                    placeholder={selectedObject ? "Выберите или введите элемент" : "Введите элемент контроля"}
                    disabled={!hasSelectedMethodology || !hasSelectedObject}
                  />
                </div>
              </>
            )}

            {/* Индикатор загрузки */}
            {loadingBlocks && (
              <div className="bg-[#0C1515]/50 rounded-xl p-5">
                <div className="flex items-center justify-center py-8">
                  <Loader2 size={32} className="animate-spin text-[#D97B54]" />
                  <span className="ml-3 text-[#646C89]">{isGazpromMethodology ? 'Загрузка техкарты...' : 'Загрузка параметров...'}</span>
                </div>
              </div>
            )}

            {/* Подсказка */}
            {!loadingBlocks && !hasSelectedElement && (
              <div className={`bg-[#0C1515]/50 rounded-xl p-5 transition-opacity ${hasSelectedMethodology && hasSelectedObject ? 'opacity-100' : 'opacity-50'}`}>
                <h3 className="text-[#D97B54] font-semibold mb-4">4. Параметры</h3>
                <p className="text-[#646C89] text-center py-4">
                  {!hasSelectedMethodology
                    ? 'Сначала выберите методику'
                    : isGazpromMethodology
                      ? 'Параметры техкарты появятся после загрузки данных.'
                      : hasSelectedObject
                      ? isGazpromMethodology
                        ? 'Выберите элемент контроля, чтобы сразу загрузить полную техкарту'
                        : 'Выберите элемент контроля для загрузки параметров'
                      : 'Сначала выберите тип объекта'}
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
                {isGazpromMethodology ? (
                  <>
                    Выбрано: <span className="text-white">{methodologyInputValue}</span>
                  </>
                ) : (
                  <>
                    Выбрано: <span className="text-white">{methodologyInputValue}</span> → <span className="text-white">{objectInputValue}</span> → <span className="text-white">{elementInputValue}</span>
                  </>
                )}
              </div>
              <button
                type="button"
                onClick={() => {
                  if (isGazpromMethodology) {
                    resetMethodologySelection();
                    return;
                  }
                  resetLoadedTechCard();
                }}
                className="text-[#D97B54] hover:text-[#D97B54]/80 text-sm transition-colors"
              >
                {isGazpromMethodology ? '← Изменить методику' : '← Изменить выбор'}
              </button>
            </div>

            {/* Все динамические блоки от бэкенда */}
            {blockTabs.length > 1 && (
              <div className="mb-5 overflow-x-auto">
                <div className="flex min-w-max gap-2 rounded-xl border border-[#646C89]/20 bg-[#0C1515]/60 p-2">
                  {blockTabs.map((tab) => {
                    const isActiveTab = tab.id === activeTab?.id;

                    return (
                      <button
                        key={tab.id}
                        type="button"
                        onClick={() => setActiveTabId(tab.id)}
                        className={`min-w-[190px] rounded-lg border px-4 py-3 text-left transition-all ${isActiveTab ? 'shadow-sm' : 'opacity-80 hover:opacity-100'}`}
                        style={{
                          borderColor: isActiveTab ? 'var(--nk-accent-primary)' : 'rgba(138, 131, 119, 0.18)',
                          backgroundColor: isActiveTab ? 'var(--nk-accent-primary-soft)' : 'rgba(12, 21, 21, 0.18)',
                        }}
                      >
                        <div className="text-sm font-semibold" style={{ color: isActiveTab ? 'var(--nk-text-primary)' : 'var(--nk-text-secondary)' }}>
                          {tab.label}
                        </div>
                        <div className="mt-1 text-xs" style={{ color: 'var(--nk-text-muted)' }}>
                          {tab.description}
                        </div>
                        <div className="mt-3 text-[11px] uppercase tracking-[0.14em]" style={{ color: isActiveTab ? 'var(--nk-accent-secondary)' : 'var(--nk-text-muted)' }}>
                          Разделов: {tab.blocks.length}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {visibleBlocks.map((block, blockIndex) => {
              const isCollapsed = collapsedBlocks[block.id];
              const isComplete = isBlockComplete(block);
              const progress = getBlockProgress(block);
              const blockTitlePrefix = Number.isFinite(Number(block.id)) ? block.id : blockIndex + 1;
              
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
                    <h3 className={`font-semibold ${blockIndex % 2 === 0 ? 'text-[#D97B54]' : 'text-[#8FB996]'}`}>
                      {blockTitlePrefix}. {block.name}
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
                                let imageSrc = resolveImageSrc(param.image || param.value.image);
                                const isFullImageMode = param.displayMode === DISPLAY_MODE_IMAGE_FULL;
                                
                                // Если это base64 без префикса data:image, добавляем его
                                if (imageSrc && !imageSrc.startsWith('data:') && !imageSrc.startsWith('http') && !imageSrc.startsWith('blob:') && !imageSrc.startsWith('/')) {
                                  // Определяем тип изображения (по умолчанию png)
                                  imageSrc = `data:image/png;base64,${imageSrc}`;
                                }
                                
                                return (
                                  <tr key={compositeKey} className="border-b border-[#646C89]/20">
                                    <td colSpan={2} className="py-4 px-2">
                                      {!isFullImageMode && (
                                        <div className="text-white text-sm mb-2">
                                        <span className="text-[#D97B54] font-mono mr-2">{compositeKey}</span>
                                        {param.name}
                                        </div>
                                      )}
                                      <div className="flex justify-center">
                                        <img 
                                          src={imageSrc} 
                                          alt={param.name}
                                          className={`rounded-lg border border-[#646C89]/30 ${
                                            isFullImageMode ? 'w-full max-w-4xl object-contain' : 'max-w-full max-h-96'
                                          }`}
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
                                  onChange={(val, selectedId) => handleParamChange(compositeKey, val, selectedId)}
                                  onCreateOption={() => handleCreateParamOption(block.id, param)}
                                  standardValues={getStandardValuesForParam(param, block.id)}
                                  typeData={getParamTypeData(param)}
                                  displayMode={param.displayMode}
                                  canCreateOption={param.canCreateOption}
                                  isCreatingOption={savingOptionKey === compositeKey}
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
                                className="flex-1 bg-[#0C1515] border border-[#646C89]/50 rounded px-3 py-1.5 text-white text-sm placeholder-[#646C89] focus:outline-none focus:border-[#D97B54]"
                              />
                              <input
                                type="text"
                                value={field.value}
                                onChange={(e) => updateCustomField(block.id, field.id, 'value', e.target.value)}
                                placeholder="Значение"
                                className="flex-1 bg-[#0C1515] border border-[#646C89]/50 rounded px-3 py-1.5 text-white text-sm placeholder-[#646C89] focus:outline-none focus:border-[#D97B54]"
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
                        className="flex items-center gap-2 px-3 py-1.5 text-[#D97B54] hover:bg-[#D97B54]/10 rounded-lg transition-colors text-sm"
                      >
                        <Plus size={16} />
                        Добавить поле
                      </button>
                      
                      <label className="flex items-center gap-2 px-3 py-1.5 text-[#D97B54] hover:bg-[#D97B54]/10 rounded-lg transition-colors text-sm cursor-pointer">
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
                ? 'bg-[#D97B54] hover:bg-[#D97B54]/80 text-white shadow-lg hover:shadow-[#D97B54]/20'
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

