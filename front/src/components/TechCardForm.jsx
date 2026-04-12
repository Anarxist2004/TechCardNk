import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import {
  ChevronDown,
  ChevronRight,
  Loader2,
  FileCheck,
  CheckCircle,
  AlertCircle,
  Plus,
  Trash2,
  Image,
  X,
  Download,
} from 'lucide-react';
import api from '../services/api';
import { buildTechCardPayload, updateTechCard } from '../data/formConfig';
import { exportTechCardToWord } from '../utils/techCardExport';

const DEFAULT_METHODOLOGY = 0;
const DISPLAY_MODE_NUMBER_ONLY = 'number_only';
const DISPLAY_MODE_IMAGE_FULL = 'image_full';
const DISPLAY_MODE_SECTION_HEADER = 'section_header';
const DISPLAY_MODE_OPERATIONS_ROW = 'operations_row';
const IMAGE_FRAME_COLOR = '#98785c';
const INLINE_IMAGE_LAYOUT_BLOCK_IDS = new Set(['2', '3']);
const PANORAMIC_SCHEME_NAME = 'Панорамное просвечивание кольцевого сварного соединения';
const DOUBLE_WALL_SCHEME_NAME = 'Кольцевое сварное соединение через две стенки';
const DISTANCE_PARAM_FRAGMENTS = [
  'расстояние от иии до поверхности',
  'контролируемого сварного соединения',
];
const SCHEME_PARAM_NAME = 'схема просвечивания';
const SCHEME_PARAM_FRAGMENT = 'схема просвечивания';
const NOMINAL_DIAMETER_PARAM_FRAGMENT = 'номинальный диаметр трубы';
const WALL_THICKNESS_PARAM_FRAGMENT = 'номинальная толщина стенки';
const FOCAL_SPOT_PARAM_FRAGMENT = 'размер фокусного пятна иии';
const SENSITIVITY_PARAM_FRAGMENT = 'чувствительность контроля';
const QUALITY_PARAM_FRAGMENT = 'уровень качества';
const PANORAMIC_SCHEME_FRAGMENTS = [
  'панорамное просвечивание',
  'кольцевого сварного соединения',
];
const DOUBLE_WALL_SCHEME_FRAGMENTS = [
  'кольцевое сварное соединение',
  'через две стенки',
];

const createLocalId = (prefix) => `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;

const normalizeUploadedImagesState = (images) => {
  if (!images || typeof images !== 'object') {
    return {};
  }

  return Object.fromEntries(
    Object.entries(images).map(([blockId, blockImages]) => [
      blockId,
      Array.isArray(blockImages)
        ? blockImages
          .filter((image) => image && image.preview)
          .map((image, index) => ({
            id: image.id || `${blockId}-image-${index}`,
            name: image.name || `Изображение ${index + 1}`,
            preview: image.preview,
          }))
        : [],
    ]),
  );
};

const buildUploadedImagesForSave = (images) => Object.fromEntries(
  Object.entries(normalizeUploadedImagesState(images))
    .map(([blockId, blockImages]) => [
      blockId,
      blockImages.map((image) => ({
        id: image.id,
        name: image.name,
        preview: image.preview,
      })),
    ])
    .filter(([, blockImages]) => blockImages.length > 0),
);

/** Одна вкладка = один блок; id стабилен для выбора активной вкладки. */
const getBlockTabId = (blockId) => String(blockId);

const buildBlockTabs = (blocks = []) => blocks.map((block) => ({
  id: getBlockTabId(block.id),
  block,
}));

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

const normalizeComparableText = (value) => String(value ?? '').trim().replace(/\s+/g, ' ').toLowerCase();

const matchesAllFragments = (value, fragments) => {
  const normalizedValue = normalizeComparableText(value);
  return normalizedValue !== '' && fragments.every((fragment) => normalizedValue.includes(fragment));
};

const parseDecimalValue = (value) => {
  if (value === null || value === undefined || value === '' || Array.isArray(value)) {
    return null;
  }

  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : null;
  }

  const normalized = String(value).trim().replace(',', '.');
  if (!normalized) {
    return null;
  }

  const parsed = Number.parseFloat(normalized);
  return Number.isFinite(parsed) ? parsed : null;
};

const parseFocalSpotMax = (value) => {
  if (value === null || value === undefined || value === '' || Array.isArray(value)) {
    return null;
  }

  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : null;
  }

  const normalized = String(value)
    .trim()
    .replace(/,/g, '.')
    .replace(/[×*XХх]/g, 'x');

  if (!normalized) {
    return null;
  }

  const matches = normalized.match(/-?\d+(?:\.\d+)?|-?\d*\.\d+/g) || [];
  if (matches.length === 0) {
    return null;
  }

  const parsedValues = matches
    .map((part) => Number.parseFloat(part))
    .filter((part) => Number.isFinite(part));

  if (parsedValues.length === 0) {
    return null;
  }

  return Math.max(...parsedValues);
};

const formatRangeNumber = (value) => {
  if (!Number.isFinite(value)) {
    return '';
  }

  return value
    .toFixed(2)
    .replace(/\.00$/, '')
    .replace(/(\.\d*[1-9])0$/, '$1');
};

const parseQualityValue = (value) => {
  if (value === null || value === undefined || Array.isArray(value)) {
    return null;
  }

  const normalized = String(value).trim().toUpperCase();
  return ['A', 'B', 'C'].includes(normalized) ? normalized : null;
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
  const rawValue = param?.value;

  if (rawValue === null || rawValue === undefined || Array.isArray(rawValue)) {
    return fallbackValue;
  }

  if (typeof rawValue === 'object') {
    if (rawValue.name !== undefined) {
      return String(rawValue.name);
    }

    if (rawValue.id !== undefined) {
      return String(rawValue.id);
    }

    return fallbackValue;
  }

  return String(rawValue);
};

const getInputValue2FromParam = (param, fallbackValue = '') => {
  const rawValue = param?.value2;

  if (rawValue === null || rawValue === undefined || Array.isArray(rawValue)) {
    return fallbackValue;
  }

  if (typeof rawValue === 'object') {
    if (rawValue.name !== undefined) {
      return String(rawValue.name);
    }

    if (rawValue.id !== undefined) {
      return String(rawValue.id);
    }

    return fallbackValue;
  }

  return String(rawValue);
};

const getSelectedIdFromParam = (param) => {
  if (param?.selectedId !== undefined && param?.selectedId !== null && param?.selectedId !== '') {
    return String(param.selectedId);
  }

  const rawValue = param?.value;
  if (rawValue && typeof rawValue === 'object' && !Array.isArray(rawValue) && rawValue.id !== undefined) {
    return String(rawValue.id);
  }

  return null;
};

const resolveImageSrc = (imageSrc) => {
  if (!imageSrc) {
    return '';
  }

  const normalizedSrc = String(imageSrc).trim();

  if (
    normalizedSrc.startsWith('data:')
    || normalizedSrc.startsWith('http://')
    || normalizedSrc.startsWith('https://')
    || normalizedSrc.startsWith('blob:')
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

const isImageParam = (param) => Boolean(
  param?.image
  || (
    param?.value
    && typeof param.value === 'object'
    && !Array.isArray(param.value)
    && param.value.image
  ),
);

/**
 * Для параметра только с картинкой и без val (и без val2/options/расширенного value) поле ввода не показываем.
 */
const imageParamExpectsValueField = (param) => {
  if (!isImageParam(param)) {
    return true;
  }
  if (param.hasVal2) {
    return true;
  }
  if (Array.isArray(param.options) && param.options.length > 0) {
    return true;
  }
  const v = param.value;
  if (v === null || v === undefined || v === '') {
    return false;
  }
  if (typeof v === 'object' && !Array.isArray(v)) {
    const keys = Object.keys(v).filter((k) => k !== 'image');
    if (keys.length === 0 && v.image) {
      return false;
    }
    return true;
  }
  return true;
};

const isSectionHeaderParam = (param) => param?.displayMode === DISPLAY_MODE_SECTION_HEADER;

const isOperationsRowParam = (param) => param?.displayMode === DISPLAY_MODE_OPERATIONS_ROW;

const isReadOnlyParam = (param) => Boolean(param?.readOnly) || isSectionHeaderParam(param) || isOperationsRowParam(param);

const isEditableParam = (param) => !isReadOnlyParam(param) && imageParamExpectsValueField(param);

const normalizeStaticValue = (value) => {
  if (value === null || value === undefined) {
    return '';
  }

  if (typeof value === 'string') {
    return value.trim();
  }

  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value);
  }

  if (Array.isArray(value)) {
    return value.map(normalizeStaticValue).filter(Boolean).join('\n');
  }

  if (typeof value === 'object') {
    if (value.image) {
      return '';
    }

    if (value.name !== undefined && value.name !== null) {
      return String(value.name).trim();
    }

    if (value.value !== undefined && value.value !== null && typeof value.value !== 'object') {
      return String(value.value).trim();
    }

    return Object.entries(value)
      .filter(([key]) => key !== 'image')
      .map(([key, nestedValue]) => {
        const text = normalizeStaticValue(nestedValue);
        return text ? `${key}: ${text}` : '';
      })
      .filter(Boolean)
      .join('\n');
  }

  return String(value).trim();
};

const getReadOnlyParamValue = (param, compositeKey, values) => {
  const hasOverrideValue = Object.prototype.hasOwnProperty.call(values, compositeKey);
  const overrideValue = values[compositeKey];
  const sourceValue = hasOverrideValue && overrideValue !== '' && overrideValue !== null && overrideValue !== undefined
    ? overrideValue
    : param.value;

  return normalizeStaticValue(sourceValue);
};

const getReadOnlyParamDisplay = (param, compositeKey, values, values2 = {}) => {
  const primary = getReadOnlyParamValue(param, compositeKey, values);
  if (!param.hasVal2) {
    return primary;
  }

  const hasOverride2 = Object.prototype.hasOwnProperty.call(values2, compositeKey);
  const override2 = values2[compositeKey];
  const secondary = hasOverride2 && override2 !== '' && override2 !== null && override2 !== undefined
    ? String(override2).trim()
    : normalizeStaticValue(param.value2);

  if (!primary && !secondary) {
    return '';
  }
  if (!secondary) {
    return primary;
  }
  if (!primary) {
    return secondary;
  }
  return `${primary} – ${secondary}`;
};

const getOperationsRowValue = (param) => {
  const rawValue = (param?.value && typeof param.value === 'object' && !Array.isArray(param.value))
    ? param.value
    : {};

  return {
    content: normalizeStaticValue(rawValue.content),
    equipment: normalizeStaticValue(rawValue.equipment),
  };
};

const buildFormStateFromBlocks = (blocks = []) => {
  const values = {};
  const values2 = {};
  const selectedIds = {};

  blocks.forEach((block) => {
    block.params.forEach((param) => {
      const compositeKey = `${block.id}.${param.id}`;
      if (isEditableParam(param)) {
        const inputValue = getInputValueFromParam(param, undefined);
        if (inputValue !== undefined) {
          values[compositeKey] = inputValue;
        }
        if (param.hasVal2) {
          const inputValue2 = getInputValue2FromParam(param, undefined);
          if (inputValue2 !== undefined) {
            values2[compositeKey] = inputValue2;
          }
        }
      }

      const selectedId = getSelectedIdFromParam(param);
      if (selectedId !== null) {
        selectedIds[compositeKey] = selectedId;
      }
    });
  });

  return { values, values2, selectedIds };
};

const buildStandardValuesCacheFromBlocks = (blocks = []) => {
  const cache = {};

  blocks.forEach((block) => {
    block.params.forEach((param) => {
      if (!isEditableParam(param)) {
        return;
      }

      const compositeKey = `${block.id}.${param.id}`;
      const optionValues = normalizeOptionValues(param.options);
      const rawValue = param.value;

      if (optionValues.length > 0) {
        cache[compositeKey] = optionValues;
        return;
      }

      if (Array.isArray(rawValue) && rawValue.length > 0) {
        cache[compositeKey] = normalizeOptionValues(rawValue);
        return;
      }

      if (
        typeof rawValue === 'object'
        && rawValue !== null
        && !Array.isArray(rawValue)
        && !isSelectedValueObject(rawValue)
      ) {
        cache[compositeKey] = Object.values(rawValue).map((item) => String(item));
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
    window.innerWidth - width - viewportPadding,
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

const validateByType = (value, typeData) => {
  if (!value || value.trim() === '') {
    return { isValid: true, error: null };
  }

  const trimmedValue = value.trim();
  const normalizedType = (typeData || 'string').toLowerCase();

  switch (normalizedType) {
    case 'int':
    case 'integer':
      if (!/^-?\d+$/.test(trimmedValue)) {
        return { isValid: false, error: 'Введите целое число' };
      }
      return { isValid: true, error: null };

    case 'double':
    case 'float':
    case 'real': {
      const normalizedNumber = trimmedValue.replace(',', '.');
      if (!/^-?\d*\.?\d+$/.test(normalizedNumber) || Number.isNaN(Number.parseFloat(normalizedNumber))) {
        return { isValid: false, error: 'Введите число, например 12.5' };
      }
      return { isValid: true, error: null };
    }

    case 'bool':
    case 'boolean': {
      const boolValues = ['true', 'false', 'да', 'нет', '1', '0', 'yes', 'no'];
      if (!boolValues.includes(trimmedValue.toLowerCase())) {
        return { isValid: false, error: 'Введите да/нет, true/false или 1/0' };
      }
      return { isValid: true, error: null };
    }

    case 'string':
    case 'text':
    default:
      return { isValid: true, error: null };
  }
};

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

const TableRowInput = ({
  paramName,
  value,
  value2 = '',
  onChange,
  onChange2,
  onCommit,
  onCreateOption,
  standardValues,
  typeData,
  displayMode,
  placeholder,
  canCreateOption,
  isCreatingOption,
  hasVal2 = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [touched, setTouched] = useState(false);
  const [touched2, setTouched2] = useState(false);
  const [dropdownStyle, setDropdownStyle] = useState(null);
  const textareaRef = React.useRef(null);
  const textarea2Ref = React.useRef(null);
  const dropdownAnchorRef = React.useRef(null);
  const skipNextBlurCommitRef = React.useRef(false);

  const validation = validateByType(value, typeData);
  const validation2 = hasVal2 ? validateByType(value2, typeData) : { isValid: true, error: null };
  const showError = touched && !validation.isValid;
  const showError2 = hasVal2 && touched2 && !validation2.isValid;
  const typeHint = getTypeHint(typeData);
  const suggestionOptions = normalizeSuggestionOptions(standardValues);
  const isNumberOnlyMode = displayMode === DISPLAY_MODE_NUMBER_ONLY;
  const trimmedValue = String(value ?? '').trim();
  const primaryPlaceholder = placeholder ?? 'Введите значение';
  const rangePlaceholder = placeholder ?? 'Значение';
  const hasExistingOption = suggestionOptions.some((option) => {
    const optionLabel = normalizeComparableText(option.label || option.value);
    return optionLabel === normalizeComparableText(trimmedValue);
  });
  const canSaveOption = Boolean(canCreateOption && onCreateOption) && trimmedValue !== '' && !hasExistingOption;
  const hasActionButtons = suggestionOptions.length > 0 || canSaveOption || isCreatingOption;

  useEffect(() => {
    // Авто‑подбор высоты полей. Если есть val2 — оба поля растягиваются до одинаковой высоты,
    // чтобы в блоке «Перечень операций» левая и правая колонки были одной высоты.
    if (!textareaRef.current) {
      return;
    }

    if (!hasVal2) {
      textareaRef.current.style.height = '0px';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
      return;
    }

    if (!textarea2Ref.current) {
      return;
    }

    textareaRef.current.style.height = '0px';
    textarea2Ref.current.style.height = '0px';

    const h1 = textareaRef.current.scrollHeight;
    const h2 = textarea2Ref.current.scrollHeight;
    const maxH = Math.max(h1, h2);

    const target = Math.max(maxH, 28);
    textareaRef.current.style.height = `${target}px`;
    textarea2Ref.current.style.height = `${target}px`;
  }, [value, value2, hasVal2]);

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

  const handleChange = (nextValue) => {
    const normalizedType = (typeData || 'string').toLowerCase();

    if ((normalizedType === 'int' || normalizedType === 'integer') && nextValue !== '' && !/^-?\d*$/.test(nextValue)) {
      return;
    }

    if (['double', 'float', 'real'].includes(normalizedType) && nextValue !== '' && !/^-?\d*[.,]?\d*$/.test(nextValue)) {
      return;
    }

    onChange(nextValue, null);
  };

  const handleChange2 = (nextValue) => {
    if (!onChange2) {
      return;
    }
    const normalizedType = (typeData || 'string').toLowerCase();

    if ((normalizedType === 'int' || normalizedType === 'integer') && nextValue !== '' && !/^-?\d*$/.test(nextValue)) {
      return;
    }

    if (['double', 'float', 'real'].includes(normalizedType) && nextValue !== '' && !/^-?\d*[.,]?\d*$/.test(nextValue)) {
      return;
    }

    onChange2(nextValue);
  };

  const handleBlur = (event, setTouchedState) => {
    setTouchedState(true);

    if (dropdownAnchorRef.current?.contains(event.relatedTarget)) {
      return;
    }

    if (skipNextBlurCommitRef.current) {
      skipNextBlurCommitRef.current = false;
      return;
    }

    onCommit?.();
  };

  const markNextBlurCommitToSkip = () => {
    skipNextBlurCommitRef.current = true;
  };

  const handleControlBlur = (event) => {
    if (dropdownAnchorRef.current?.contains(event.relatedTarget)) {
      return;
    }

    if (skipNextBlurCommitRef.current) {
      skipNextBlurCommitRef.current = false;
      return;
    }

    onCommit?.();
  };

  return (
    <tr className="border-b border-[#646C89]/20 hover:bg-[#646C89]/10">
      {!isNumberOnlyMode && (
        <td
          className="py-2 px-2 text-white text-sm align-top"
          style={{ width: '300px', minWidth: '300px', maxWidth: '300px' }}
        >
          {paramName}
          {typeHint && <span className="ml-1 text-xs text-[#646C89]">({typeHint})</span>}
        </td>
      )}
      <td
        colSpan={isNumberOnlyMode ? 2 : undefined}
        className="py-2 px-2 align-top"
        style={isNumberOnlyMode ? undefined : {
          width: hasVal2 ? '560px' : '400px',
          minWidth: hasVal2 ? '560px' : '400px',
        }}
      >
        <div className={isNumberOnlyMode ? 'flex items-start gap-3 w-full' : ''}>
          <div
            ref={dropdownAnchorRef}
            className={isNumberOnlyMode ? 'relative flex-1 min-w-0' : hasVal2 ? 'relative w-full min-w-0' : 'relative'}
          >
            {hasVal2 ? (
              <div className="w-full space-y-1">
                <div className="flex flex-row items-end gap-2 w-full">
                  <div className="flex-1 min-w-0">
                    <div className="relative">
                      <textarea
                        ref={textareaRef}
                        value={value}
                        onChange={(event) => handleChange(event.target.value)}
                        onBlur={(event) => handleBlur(event, setTouched)}
                        placeholder={rangePlaceholder}
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
                          onBlur={handleControlBlur}
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
                          onClick={() => setIsOpen((prev) => !prev)}
                          onBlur={handleControlBlur}
                          className="absolute top-1/2 -translate-y-1/2 right-2 text-[#646C89] hover:text-[#D97B54]"
                        >
                          <ChevronDown size={16} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
                        </button>
                      )}
                    </div>
                  </div>
                  <span className="text-[#646C89] shrink-0 select-none pb-2" aria-hidden>–</span>
                  <div className="relative flex-1 min-w-0">
                    <textarea
                      ref={textarea2Ref}
                      value={value2}
                      onChange={(event) => handleChange2(event.target.value)}
                      onBlur={(event) => handleBlur(event, setTouched2)}
                      placeholder="Значение"
                      rows={1}
                      className={`
                        w-full bg-[#0C1515] border
                        rounded px-3 py-1.5 pr-3
                        text-white placeholder-[#646C89]
                        focus:outline-none
                        transition-colors text-sm
                        resize-none
                        ${showError2
                          ? 'border-red-500 focus:border-red-500'
                          : 'border-[#646C89]/50 focus:border-[#D97B54]'
                        }
                      `}
                      style={{ height: 'auto', minHeight: '28px', overflow: 'hidden', lineHeight: '1.4' }}
                    />
                  </div>
                </div>
                <div className="flex flex-row gap-2">
                  {showError && (
                    <span className="text-xs text-red-500 flex-1 min-w-0">{validation.error}</span>
                  )}
                  {showError2 && (
                    <span className="text-xs text-red-500 flex-1 min-w-0">{validation2.error}</span>
                  )}
                </div>
              </div>
            ) : (
              <>
                <textarea
                  ref={textareaRef}
                  value={value}
                  onChange={(event) => handleChange(event.target.value)}
                  onBlur={(event) => handleBlur(event, setTouched)}
                  placeholder={primaryPlaceholder}
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
                    onBlur={handleControlBlur}
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
                    onClick={() => setIsOpen((prev) => !prev)}
                    onBlur={handleControlBlur}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-[#646C89] hover:text-[#D97B54]"
                  >
                    <ChevronDown size={16} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
                  </button>
                )}
                {showError && (
                  <span className="text-xs text-red-500 mt-0.5 block">{validation.error}</span>
                )}
              </>
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
                  {suggestionOptions.map((option, index) => (
                    <button
                      key={`${option.id ?? option.value}_${index}`}
                      type="button"
                      onMouseDown={markNextBlurCommitToSkip}
                      onClick={() => {
                        onChange(option.value, option.id);
                        onCommit?.();
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
              document.body,
            )}
          </div>
        </div>
      </td>
    </tr>
  );
};

const ReadOnlyTableRow = ({ param, value }) => {
  if (isSectionHeaderParam(param)) {
    return (
      <tr className="border-b border-[#646C89]/20 bg-[#646C89]/10">
        <td colSpan={2} className="py-2 px-2 text-sm font-semibold text-white">
          {param.name}
        </td>
      </tr>
    );
  }

  const isNumberOnlyMode = param.displayMode === DISPLAY_MODE_NUMBER_ONLY;

  return (
    <tr className="border-b border-[#646C89]/20">
      {!isNumberOnlyMode && (
        <td
          className="py-2 px-2 text-white text-sm align-top"
          style={{ width: '300px', minWidth: '300px', maxWidth: '300px' }}
        >
          {param.name}
        </td>
      )}
      <td
        colSpan={isNumberOnlyMode ? 2 : undefined}
        className="py-2 px-2 align-top"
        style={isNumberOnlyMode ? undefined : { width: '400px', minWidth: '400px' }}
      >
        <div className="whitespace-pre-wrap text-sm text-white">{value || '-'}</div>
      </td>
    </tr>
  );
};

const OperationsTable = ({ block }) => {
  const operationRows = (block?.params || []).filter(isOperationsRowParam);

  if (operationRows.length === 0) {
    return null;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse table-fixed">
        <thead>
          <tr className="border-b border-[#646C89]/30">
            <th className="w-[50%] py-2 px-2 text-left text-[#646C89] text-xs font-medium">
              Наименование операции / Содержание, основные требования
            </th>
            <th className="w-[26%] py-2 px-2 text-left text-[#646C89] text-xs font-medium">Оборудование и инструмент</th>
          </tr>
        </thead>
        <tbody>
          {operationRows.map((param) => {
            const { content, equipment } = getOperationsRowValue(param);
            const rowKey = `${block.id}.${param.id}`;
            const operationName = param.name || '-';

            return (
              <tr key={rowKey} className="border-b border-[#646C89]/20 align-top">
                <td className="py-2 px-2 text-sm text-white whitespace-pre-wrap">
                  <div className="font-semibold mb-1">{operationName}</div>
                  {content || '-'}
                </td>
                <td className="py-2 px-2 text-sm text-white whitespace-pre-wrap">
                  {equipment || '-'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

const TechCardForm = ({ initialSavedCard = null }) => {
  const [blocks, setBlocks] = useState([]);
  const [loadingBlocks, setLoadingBlocks] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [objectType, setObjectType] = useState(null);
  const [paramValues, setParamValues] = useState({});
  const [paramValues2, setParamValues2] = useState({});
  const [selectedOptionIds, setSelectedOptionIds] = useState({});
  const paramValuesRef = useRef({});
  const paramValues2Ref = useRef({});
  const selectedOptionIdsRef = useRef({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [collapsedBlocks, setCollapsedBlocks] = useState({});
  const [customFields, setCustomFields] = useState({});
  const [uploadedImages, setUploadedImages] = useState({});
  const [standardValuesCache, setStandardValuesCache] = useState({});
  const [savingOptionKey, setSavingOptionKey] = useState(null);
  const [activeTabId, setActiveTabId] = useState('');
  const [savedCardId, setSavedCardId] = useState(initialSavedCard?.id ?? null);
  const [cardName, setCardName] = useState(initialSavedCard?.cardName || initialSavedCard?.name || '');
  const paramSyncTimerRef = useRef(null);
  const clearParamSyncTimer = () => {
    if (paramSyncTimerRef.current !== null) {
      clearTimeout(paramSyncTimerRef.current);
      paramSyncTimerRef.current = null;
    }
  };

  const resetLoadedTechCard = () => {
    setBlocks([]);
    setParamValues({});
    setParamValues2({});
    setSelectedOptionIds({});
    paramValuesRef.current = {};
    paramValues2Ref.current = {};
    selectedOptionIdsRef.current = {};
    setObjectType(null);
    setCollapsedBlocks({});
    setCustomFields({});
    setUploadedImages({});
    setStandardValuesCache({});
    setActiveTabId('');
    setSavedCardId(null);
    setCardName('');
  };

  const applyLoadedTechCard = (data) => {
    const nextBlocks = data.blocks || [];
    const { values, values2, selectedIds } = buildFormStateFromBlocks(nextBlocks);
    const nextTabs = buildBlockTabs(nextBlocks);

    setBlocks(nextBlocks);
    setObjectType(data.type || null);
    setParamValues(values);
    setParamValues2(values2);
    setSelectedOptionIds(selectedIds);
    paramValuesRef.current = values;
    paramValues2Ref.current = values2;
    selectedOptionIdsRef.current = selectedIds;
    setStandardValuesCache(buildStandardValuesCacheFromBlocks(nextBlocks));
    setActiveTabId((prev) => {
      if (nextTabs.length === 0) {
        return '';
      }
      const prevStr = prev != null && prev !== '' ? String(prev) : '';
      if (prevStr && nextTabs.some((t) => String(t.id) === prevStr)) {
        return prevStr;
      }
      return nextTabs[0].id;
    });
    setLoadError('');
  };

  const applySavedTechCard = (savedCard) => {
    if (!savedCard?.techCard) {
      resetLoadedTechCard();
      setLoadError('Не удалось прочитать сохранённую карту.');
      return;
    }

    applyLoadedTechCard(savedCard.techCard);
    setCustomFields(savedCard.customFields || {});
    setUploadedImages(normalizeUploadedImagesState(savedCard.uploadedImages));
    setSavedCardId(savedCard.id ?? null);
    setCardName(savedCard.cardName || savedCard.name || '');
  };

  const buildStoredTechCardSnapshot = (cardData) => {
    const sourceBlocks = cardData?.blocks || blocks;
    const sourceType = cardData?.type ?? objectType;
    const { values, values2, selectedIds } = buildFormStateFromBlocks(sourceBlocks);

    return {
      cardName: String(cardName || '').trim(),
      techCard: buildTechCardPayload(
        sourceType,
        DEFAULT_METHODOLOGY,
        sourceBlocks,
        values,
        selectedIds,
        values2,
      ),
      customFields,
      uploadedImages: buildUploadedImagesForSave(uploadedImages),
    };
  };

  const saveCurrentTechCard = async (cardData) => {
    const saved = await api.saveTechCard({
      id: savedCardId,
      name: String(cardName || '').trim(),
      data: buildStoredTechCardSnapshot(cardData),
    });

    if (saved?.id !== undefined && saved?.id !== null) {
      setSavedCardId(saved.id);
    }
    if (saved?.name) {
      setCardName(saved.name);
    }

    return saved;
  };

  const loadTechCard = async () => {
    clearParamSyncTimer();
    setLoadingBlocks(true);
    setLoadError('');

    try {
      const data = await api.getTemplate(DEFAULT_METHODOLOGY);
      applyLoadedTechCard(data);
    } catch (error) {
      console.error('Ошибка загрузки шаблона техкарты:', error);
      resetLoadedTechCard();
      setLoadError('Не удалось загрузить шаблон техкарты.');
    } finally {
      setLoadingBlocks(false);
    }
  };

  useEffect(() => {
    clearParamSyncTimer();

    if (initialSavedCard?.techCard) {
      applySavedTechCard(initialSavedCard);
      setLoadingBlocks(false);
      return;
    }

    void loadTechCard();
  }, [initialSavedCard]);

  useEffect(() => () => {
    if (paramSyncTimerRef.current !== null) {
      clearTimeout(paramSyncTimerRef.current);
      paramSyncTimerRef.current = null;
    }
  }, []);

  useEffect(() => {
    const availableTabs = buildBlockTabs(blocks);

    if (availableTabs.length === 0) {
      if (activeTabId !== '') {
        setActiveTabId('');
      }
      return;
    }

    const activeStr = activeTabId != null && activeTabId !== '' ? String(activeTabId) : '';
    if (
      !activeStr
      || !availableTabs.some((tab) => String(tab.id) === activeStr)
    ) {
      setActiveTabId(availableTabs[0].id);
    }
  }, [blocks, activeTabId]);

  const addCustomField = (blockId) => {
    setCustomFields((prev) => ({
      ...prev,
      [blockId]: [
        ...(prev[blockId] || []),
        { id: createLocalId('custom'), name: '', value: '' },
      ],
    }));
  };

  const updateCustomField = (blockId, fieldId, field, value) => {
    setCustomFields((prev) => ({
      ...prev,
      [blockId]: (prev[blockId] || []).map((item) => (
        item.id === fieldId ? { ...item, [field]: value } : item
      )),
    }));
  };

  const deleteCustomField = (blockId, fieldId) => {
    setCustomFields((prev) => ({
      ...prev,
      [blockId]: (prev[blockId] || []).filter((item) => item.id !== fieldId),
    }));
  };

  const handleImageUpload = (blockId, event) => {
    const files = Array.from(event.target.files || []);

    files.forEach((file) => {
      if (!file.type.startsWith('image/')) {
        return;
      }

      const reader = new FileReader();
      reader.onload = (loadEvent) => {
        if (!loadEvent.target?.result) {
          return;
        }

        setUploadedImages((prev) => ({
          ...prev,
          [blockId]: [
            ...(prev[blockId] || []),
            {
              id: createLocalId('img'),
              file,
              preview: loadEvent.target.result,
              name: file.name,
            },
          ],
        }));
      };
      reader.readAsDataURL(file);
    });

    event.target.value = '';
  };

  const deleteImage = (blockId, imageId) => {
    setUploadedImages((prev) => ({
      ...prev,
      [blockId]: (prev[blockId] || []).filter((image) => image.id !== imageId),
    }));
  };

  const toggleBlockCollapse = (blockId) => {
    setCollapsedBlocks((prev) => ({
      ...prev,
      [blockId]: !prev[blockId],
    }));
  };

  const isBlockComplete = (block) => {
    const progressParams = (block.params || []).filter(isEditableParam);

    if (progressParams.length === 0) {
      return true;
    }

    return progressParams.every((param) => {
      const compositeKey = `${block.id}.${param.id}`;
      const value = paramValues[compositeKey];
      const primaryOk = value && String(value).trim() !== '';
      if (!param.hasVal2) {
        return primaryOk;
      }
      const value2 = paramValues2[compositeKey];
      return primaryOk && value2 && String(value2).trim() !== '';
    });
  };

  const getBlockProgress = (block) => {
    const progressParams = (block.params || []).filter(isEditableParam);

    if (progressParams.length === 0) {
      return { filled: 0, total: 0 };
    }

    const total = progressParams.length;
    const filled = progressParams.filter((param) => {
      const compositeKey = `${block.id}.${param.id}`;
      const value = paramValues[compositeKey];
      const primaryOk = value && String(value).trim() !== '';
      if (!param.hasVal2) {
        return primaryOk;
      }
      const value2 = paramValues2[compositeKey];
      return primaryOk && value2 && String(value2).trim() !== '';
    }).length;

    return { filled, total };
  };

  const getParamByCompositeKey = (compositeKey) => {
    const [blockId, ...paramParts] = String(compositeKey).split('.');
    const paramId = paramParts.join('.');
    const matchedBlock = blocks.find((block) => String(block.id) === blockId);

    if (!matchedBlock) {
      return null;
    }

    return matchedBlock.params.find((param) => String(param.id) === paramId) || null;
  };

  const syncTechCardToServer = async (vals, vals2, selIds) => {
    try {
      const techCardPayload = buildTechCardPayload(
        objectType,
        DEFAULT_METHODOLOGY,
        blocks,
        vals,
        selIds,
        vals2,
      );

      const result = await updateTechCard(techCardPayload);
      if (result.blocks && result.blocks.length > 0) {
        applyLoadedTechCard(result);
      }
    } catch (error) {
      console.error('Ошибка при обновлении параметра:', error);
    }
  };

  const resolveMatchingStandardOption = (standardValues, rawValue) => {
    const normalizedValue = normalizeComparableText(rawValue);

    if (!normalizedValue) {
      return null;
    }

    return normalizeSuggestionOptions(standardValues).find((option) => (
      normalizeComparableText(option.value) === normalizedValue
    )) || null;
  };

  const commitParamChange = async (compositeKey) => {
    clearParamSyncTimer();

    const updatedSelectedOptionIds = { ...selectedOptionIdsRef.current };
    const currentValue = paramValuesRef.current[compositeKey];
    const normalizedValue = normalizeComparableText(currentValue);

    if (!normalizedValue) {
      delete updatedSelectedOptionIds[compositeKey];
    } else {
      const param = getParamByCompositeKey(compositeKey);
      const [blockId] = String(compositeKey).split('.');
      const matchedOption = param
        ? resolveMatchingStandardOption(getStandardValuesForParam(param, blockId), currentValue)
        : null;

      if (matchedOption?.id !== null && matchedOption?.id !== undefined && matchedOption?.id !== '') {
        updatedSelectedOptionIds[compositeKey] = String(matchedOption.id);
      } else {
        delete updatedSelectedOptionIds[compositeKey];
      }
    }

    selectedOptionIdsRef.current = updatedSelectedOptionIds;
    setSelectedOptionIds(updatedSelectedOptionIds);

    await syncTechCardToServer(
      paramValuesRef.current,
      paramValues2Ref.current,
      updatedSelectedOptionIds,
    );
  };

  const handleParamChange = (compositeKey, value, selectedOptionId = null) => {
    const updatedValues = {
      ...paramValuesRef.current,
      [compositeKey]: value,
    };
    const updatedSelectedOptionIds = { ...selectedOptionIdsRef.current };

    if (selectedOptionId !== null && selectedOptionId !== undefined && selectedOptionId !== '') {
      updatedSelectedOptionIds[compositeKey] = String(selectedOptionId);
    } else {
      delete updatedSelectedOptionIds[compositeKey];
    }

    paramValuesRef.current = updatedValues;
    selectedOptionIdsRef.current = updatedSelectedOptionIds;
    setParamValues(updatedValues);
    setSelectedOptionIds(updatedSelectedOptionIds);
  };

  const handleParamValue2Change = (compositeKey, value2) => {
    const updatedValues2 = {
      ...paramValues2Ref.current,
      [compositeKey]: value2,
    };
    paramValues2Ref.current = updatedValues2;
    setParamValues2(updatedValues2);
  };

  const handleCreateParamOption = async (blockId, param) => {
    const compositeKey = `${blockId}.${param.id}`;
    const currentValue = String(paramValuesRef.current[compositeKey] ?? '').trim();

    if (!currentValue) {
      return;
    }

    setSavingOptionKey(compositeKey);

    try {
      const techCardPayload = buildTechCardPayload(
        objectType,
        DEFAULT_METHODOLOGY,
        blocks,
        paramValuesRef.current,
        selectedOptionIdsRef.current,
        paramValues2Ref.current,
      );

      const result = await api.createParamOption({
        methodology: DEFAULT_METHODOLOGY,
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

      const updatedValues = {
        ...paramValuesRef.current,
        [compositeKey]: savedName,
      };
      paramValuesRef.current = updatedValues;
      setParamValues(updatedValues);

      const updatedSelectedOptionIds = { ...selectedOptionIdsRef.current };
      if (savedId !== null && savedId !== undefined) {
        updatedSelectedOptionIds[compositeKey] = String(savedId);
      } else {
        delete updatedSelectedOptionIds[compositeKey];
      }
      selectedOptionIdsRef.current = updatedSelectedOptionIds;
      setSelectedOptionIds(updatedSelectedOptionIds);

      setStandardValuesCache((prev) => {
        const currentOptions = prev[compositeKey]?.length > 0
          ? prev[compositeKey]
          : normalizeOptionValues(param.options);

        const optionExists = currentOptions.some((option) => {
          if (typeof option === 'object' && option !== null) {
            return normalizeComparableText(option.name) === normalizeComparableText(savedName);
          }

          return normalizeComparableText(option) === normalizeComparableText(savedName);
        });

        if (optionExists) {
          return prev;
        }

        return {
          ...prev,
          [compositeKey]: [...currentOptions, savedOption],
        };
      });

      await commitParamChange(compositeKey);

      alert(result.message || 'Значение сохранено');
    } catch (error) {
      console.error('Ошибка сохранения значения:', error);
      alert(`Ошибка сохранения значения: ${error.message}`);
    } finally {
      setSavingOptionKey(null);
    }
  };

  const getStandardValuesForParam = (param, blockId) => {
    if (!isEditableParam(param)) {
      return [];
    }

    const compositeKey = `${blockId}.${param.id}`;

    if (standardValuesCache[compositeKey]?.length > 0) {
      return standardValuesCache[compositeKey];
    }

    const optionValues = normalizeOptionValues(param.options);
    if (optionValues.length > 0) {
      return optionValues;
    }

    const rawValue = param.value;
    if (Array.isArray(rawValue)) {
      return normalizeOptionValues(rawValue);
    }

    if (typeof rawValue === 'object' && rawValue !== null && !Array.isArray(rawValue)) {
      if (isSelectedValueObject(rawValue)) {
        return [];
      }

      return Object.values(rawValue).map((item) => String(item));
    }

    return [];
  };

  const getParamTypeData = (param) => {
    if (param.typeData) {
      return param.typeData;
    }

    if (Array.isArray(param.options) && param.options.length > 0) {
      const firstOption = param.options[0];
      if (typeof firstOption === 'number') {
        return Number.isInteger(firstOption) ? 'int' : 'double';
      }
      if (typeof firstOption === 'boolean') {
        return 'bool';
      }
    }

    if (Array.isArray(param.value) && param.value.length > 0) {
      const firstValue = param.value[0];
      if (typeof firstValue === 'number') {
        return Number.isInteger(firstValue) ? 'int' : 'double';
      }
      if (typeof firstValue === 'boolean') {
        return 'bool';
      }
    }

    if (typeof param.value === 'number') {
      return Number.isInteger(param.value) ? 'int' : 'double';
    }

    if (typeof param.value === 'boolean') {
      return 'bool';
    }

    return 'string';
  };

  const getCurrentParamValue = (blockId, param) => {
    const compositeKey = `${blockId}.${param.id}`;
    if (Object.prototype.hasOwnProperty.call(paramValues, compositeKey)) {
      return paramValues[compositeKey];
    }
    return param.value;
  };

  const findCurrentParamValueByName = (paramNames) => {
    const names = Array.isArray(paramNames) ? paramNames : [paramNames];

    for (const block of blocks) {
      for (const param of block.params || []) {
        if (!names.includes(param.name)) {
          continue;
        }
        return getCurrentParamValue(block.id, param);
      }
    }

    return null;
  };

  const findCurrentParamValueByFragment = (fragment) => {
    const normalizedFragment = normalizeComparableText(fragment);

    for (const block of blocks) {
      for (const param of block.params || []) {
        if (!normalizeComparableText(param.name).includes(normalizedFragment)) {
          continue;
        }
        return getCurrentParamValue(block.id, param);
      }
    }

    return null;
  };

  const buildPanoramicDistancePlaceholder = () => {
    const outerDiameter = parseDecimalValue(findCurrentParamValueByFragment(NOMINAL_DIAMETER_PARAM_FRAGMENT));
    const wallThickness = parseDecimalValue(findCurrentParamValueByFragment(WALL_THICKNESS_PARAM_FRAGMENT));
    const sensitivity = parseDecimalValue(findCurrentParamValueByFragment(SENSITIVITY_PARAM_FRAGMENT));
    const focalSpot = parseFocalSpotMax(findCurrentParamValueByFragment(FOCAL_SPOT_PARAM_FRAGMENT));

    if (
      !Number.isFinite(outerDiameter)
      || !Number.isFinite(wallThickness)
      || !Number.isFinite(sensitivity)
      || !Number.isFinite(focalSpot)
      || outerDiameter <= 0
      || wallThickness < 0
      || sensitivity <= 0
    ) {
      return null;
    }

    const innerDiameter = outerDiameter - (2 * wallThickness);
    if (!(innerDiameter > 0) || !(outerDiameter > innerDiameter) || (innerDiameter / outerDiameter) < 0.8) {
      return null;
    }

    const minDistance = (focalSpot * (outerDiameter - innerDiameter)) / sensitivity;
    const maxDistance = innerDiameter / 2;
    if (!Number.isFinite(minDistance) || !Number.isFinite(maxDistance)) {
      return null;
    }

    return `${formatRangeNumber(minDistance)}<f<=${formatRangeNumber(maxDistance)}`;
  };

  const buildDoubleWallDistancePlaceholder = () => {
    const outerDiameter = parseDecimalValue(findCurrentParamValueByFragment(NOMINAL_DIAMETER_PARAM_FRAGMENT));
    const wallThickness = parseDecimalValue(findCurrentParamValueByFragment(WALL_THICKNESS_PARAM_FRAGMENT));
    const sensitivity = parseDecimalValue(findCurrentParamValueByFragment(SENSITIVITY_PARAM_FRAGMENT));
    const focalSpot = parseFocalSpotMax(findCurrentParamValueByFragment(FOCAL_SPOT_PARAM_FRAGMENT));
    const quality = parseQualityValue(findCurrentParamValueByFragment(QUALITY_PARAM_FRAGMENT));

    if (
      !Number.isFinite(outerDiameter)
      || !Number.isFinite(wallThickness)
      || !Number.isFinite(sensitivity)
      || !Number.isFinite(focalSpot)
      || !quality
      || outerDiameter <= 0
      || wallThickness < 0
      || sensitivity <= 0
    ) {
      return null;
    }

    const innerDiameter = outerDiameter - (2 * wallThickness);
    if (!(innerDiameter > 0) || !(outerDiameter > innerDiameter)) {
      return null;
    }

    const imageClassFactor = quality === 'A'
      ? 1.2
      : quality === 'B'
        ? 1.1
        : 1.5;
    const radiationThickness = 2 * wallThickness;

    let cFactorMultiplier = null;
    if (quality === 'A') {
      cFactorMultiplier = radiationThickness <= 100 ? 2 : 3;
    } else if (quality === 'B') {
      if (radiationThickness <= 50) {
        cFactorMultiplier = 2;
      } else if (radiationThickness <= 100) {
        cFactorMultiplier = 3;
      } else {
        cFactorMultiplier = 4;
      }
    } else if (quality === 'C') {
      cFactorMultiplier = 2;
    }

    if (!Number.isFinite(cFactorMultiplier)) {
      return null;
    }

    const cFactor = (cFactorMultiplier * focalSpot) / sensitivity;
    const minDistance = Math.max(
      0,
      (1.2 * cFactor * imageClassFactor * wallThickness) - ((outerDiameter + innerDiameter) / 2),
    );

    return `f>=${formatRangeNumber(minDistance)}`;
  };

  const getDistanceFieldPlaceholder = (param) => {
    if (param.placeholder !== null && param.placeholder !== undefined && String(param.placeholder) !== '') {
      return param.placeholder;
    }

    const normalizedParamName = normalizeComparableText(param.name);
    if (!DISTANCE_PARAM_FRAGMENTS.every((fragment) => normalizedParamName.includes(fragment))) {
      return null;
    }

    const selectedScheme = findCurrentParamValueByName(SCHEME_PARAM_NAME)
      ?? findCurrentParamValueByFragment(SCHEME_PARAM_FRAGMENT);
    const normalizedScheme = normalizeComparableText(selectedScheme);
    if (
      normalizedScheme === normalizeComparableText(PANORAMIC_SCHEME_NAME)
      || matchesAllFragments(normalizedScheme, PANORAMIC_SCHEME_FRAGMENTS)
    ) {
      return buildPanoramicDistancePlaceholder();
    }

    if (
      normalizedScheme === normalizeComparableText(DOUBLE_WALL_SCHEME_NAME)
      || matchesAllFragments(normalizedScheme, DOUBLE_WALL_SCHEME_FRAGMENTS)
    ) {
      return buildDoubleWallDistancePlaceholder();
    }

    return null;
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);

    try {
      const techCardPayload = buildTechCardPayload(
        objectType,
        DEFAULT_METHODOLOGY,
        blocks,
        paramValues,
        selectedOptionIds,
        paramValues2,
      );

      const result = await updateTechCard(techCardPayload);
      if (result.blocks && result.blocks.length > 0) {
        applyLoadedTechCard(result);
      }

      const savedCard = await saveCurrentTechCard(
        result.blocks && result.blocks.length > 0 ? result : null,
      );

      alert(`Карта успешно обработана и сохранена${savedCard?.name ? `: ${savedCard.name}` : '!'}`);
    } catch (error) {
      console.error('Ошибка обработки карты:', error);
      alert(`Ошибка при обработке карты: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleExport = async () => {
    if (blocks.length === 0 || isExporting) {
      return;
    }

    setIsExporting(true);

    try {
      await exportTechCardToWord({
        title: String(cardName || '').trim() || 'Технологическая карта',
        methodologyName: '',
        objectName: '',
        elementName: '',
        blocks,
        paramValues,
        paramValues2,
        customFields,
        uploadedImages,
      });
    } catch (error) {
      console.error('Ошибка экспорта техкарты:', error);
      alert(`Ошибка экспорта техкарты: ${error.message}`);
    } finally {
      setIsExporting(false);
    }
  };

  const isFormValid = () => {
    if (blocks.length === 0) {
      return false;
    }

    let allParamsValid = true;

    blocks.forEach((block) => {
      block.params.forEach((param) => {
        if (!isEditableParam(param)) {
          return;
        }

        const compositeKey = `${block.id}.${param.id}`;
        const value = paramValues[compositeKey] || '';
        const validation = validateByType(value, getParamTypeData(param));
        if (!validation.isValid) {
          allParamsValid = false;
        }
        if (param.hasVal2) {
          const v2 = paramValues2[compositeKey] || '';
          const validation2 = validateByType(v2, getParamTypeData(param));
          if (!validation2.isValid) {
            allParamsValid = false;
          }
        }
      });
    });

    return allParamsValid;
  };

  const hasBlocks = blocks.length > 0;
  const blockTabs = buildBlockTabs(blocks);
  const activeBlockTab = blockTabs.find((tab) => tab.id === activeTabId) || blockTabs[0] || null;
  const visibleBlocks = activeBlockTab?.block
    ? [activeBlockTab.block]
    : blocks;

  return (
    <div className="bg-[#21262F] rounded-2xl p-6 md:p-8">
      <h2 className="text-2xl font-bold text-white mb-6 pb-4 border-b border-[#646C89]/30">
        Технологическая карта
      </h2>

      <div className="mb-6">
        <label className="mb-2 block text-sm font-medium text-[#646C89]" htmlFor="tech-card-name">
          Название технологической карты
        </label>
        <input
          id="tech-card-name"
          type="text"
          value={cardName}
          onChange={(event) => setCardName(event.target.value)}
          placeholder="Например: ТК трубопровод DN500"
          className="w-full rounded-xl border border-[#646C89]/40 bg-[#0C1515] px-4 py-3 text-white placeholder-[#646C89] focus:border-[#D97B54] focus:outline-none"
        />
      </div>

      <div className="space-y-6">
        {loadingBlocks && !hasBlocks && (
          <div className="bg-[#0C1515]/50 rounded-xl p-5">
            <div className="flex items-center justify-center py-8">
              <Loader2 size={32} className="animate-spin text-[#D97B54]" />
              <span className="ml-3 text-[#646C89]">Загрузка шаблона...</span>
            </div>
          </div>
        )}

        {!loadingBlocks && !hasBlocks && (
          <div className="bg-[#0C1515]/50 rounded-xl p-5 text-center">
            <p className="text-white text-lg">
              {loadError || 'Техкарта не загрузилась.'}
            </p>
            <p className="text-[#646C89] mt-2">Проверьте backend и повторите загрузку ещё раз.</p>
          </div>
        )}

        {hasBlocks && (
          <>
            {blockTabs.length > 0 && (
              <div className="overflow-x-auto pb-1">
                <div className="flex min-w-max gap-2 rounded-xl border border-[#646C89]/20 bg-[#0C1515]/60 p-2">
                  {blockTabs.map((tab) => {
                    const { block: tabBlock } = tab;
                    const isActiveTab = tab.id === activeBlockTab?.id;
                    const blockProgress = getBlockProgress(tabBlock);
                    const blockDone = isBlockComplete(tabBlock);
                    const noEditable = blockProgress.total === 0;
                    const tabTitle = `${Number.isFinite(Number(tabBlock.id)) ? tabBlock.id : '—'}. ${tabBlock.name || 'Блок'}`;

                    return (
                      <button
                        key={tab.id}
                        type="button"
                        onClick={() => setActiveTabId(tab.id)}
                        className={`min-w-[160px] max-w-[260px] rounded-lg border px-3 py-2.5 text-left transition-all ${isActiveTab ? 'shadow-sm' : 'opacity-80 hover:opacity-100'}`}
                        style={{
                          borderColor: isActiveTab ? 'var(--nk-accent-primary)' : 'rgba(138, 131, 119, 0.18)',
                          backgroundColor: isActiveTab ? 'var(--nk-accent-primary-soft)' : 'rgba(12, 21, 21, 0.18)',
                        }}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div
                            className="text-sm font-semibold leading-snug line-clamp-2"
                            style={{ color: isActiveTab ? 'var(--nk-text-primary)' : 'var(--nk-text-secondary)' }}
                            title={tabTitle}
                          >
                            {tabTitle}
                          </div>
                          {noEditable ? (
                            <span className="shrink-0 text-[10px] uppercase tracking-wide" style={{ color: 'var(--nk-text-muted)' }}>—</span>
                          ) : blockDone ? (
                            <CheckCircle size={16} className="shrink-0" style={{ color: 'var(--nk-accent-secondary)' }} />
                          ) : (
                            <AlertCircle size={16} className="shrink-0" style={{ color: 'var(--nk-accent-primary)' }} />
                          )}
                        </div>
                        <div className="mt-2 flex items-center justify-between gap-2 text-[11px]" style={{ color: 'var(--nk-text-muted)' }}>
                          <span>
                            {noEditable
                              ? 'Нет обязательных полей'
                              : blockDone
                                ? 'Все параметры указаны'
                                : 'Есть незаполненные'}
                          </span>
                          {!noEditable && (
                            <span className="tabular-nums shrink-0">
                              {blockProgress.filled}/{blockProgress.total}
                            </span>
                          )}
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
              const operationRows = block.params.filter(isOperationsRowParam);
              const regularParams = block.params.filter((param) => !isOperationsRowParam(param));
              const hasRegularParams = regularParams.length > 0;
              const hasOperationRows = operationRows.length > 0;

              return (
                <div key={block.id} className="bg-[#0C1515]/50 rounded-xl p-5">
                  <div
                    className="flex items-center justify-between cursor-pointer select-none"
                    onClick={() => toggleBlockCollapse(block.id)}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-[#646C89] transition-transform">
                        {isCollapsed ? <ChevronRight size={20} /> : <ChevronDown size={20} />}
                      </span>
                      <h3 className={`font-semibold ${blockIndex % 2 === 0 ? 'text-[#D97B54]' : 'text-[#8FB996]'}`}>
                        {blockTitlePrefix}. {block.name}
                      </h3>
                    </div>

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

                  {!isCollapsed && (
                    <div className="mt-4">
                      {hasRegularParams ? (
                        <div className="overflow-x-auto">
                          <table className="w-full border-collapse table-auto">
                            <thead>
                              <tr className="border-b border-[#646C89]/30">
                                <th className="text-left text-[#646C89] text-xs font-medium py-2 px-2 whitespace-nowrap">Параметр</th>
                                <th className="text-left text-[#646C89] text-xs font-medium py-2 px-2">Значение</th>
                              </tr>
                            </thead>
                            <tbody>
                              {regularParams.map((param) => {
                                const compositeKey = `${block.id}.${param.id}`;

                                if (isImageParam(param)) {
                                  let imageSrc = resolveImageSrc(param.image || param.value.image);
                                  const isFullImageMode = param.displayMode === DISPLAY_MODE_IMAGE_FULL;
                                  const usesInlineImageLayout = INLINE_IMAGE_LAYOUT_BLOCK_IDS.has(String(block.id));
                                  const showImageLabel = !usesInlineImageLayout && !isFullImageMode;

                                  if (
                                    imageSrc
                                    && !imageSrc.startsWith('data:')
                                    && !imageSrc.startsWith('http')
                                    && !imageSrc.startsWith('blob:')
                                    && !imageSrc.startsWith('/')
                                  ) {
                                    imageSrc = `data:image/png;base64,${imageSrc}`;
                                  }

                                  const imageRow = (
                                    <tr key={`${compositeKey}-img`} className="border-b border-[#646C89]/20">
                                      <td colSpan={2} className="py-4 px-2">
                                        {showImageLabel && (
                                          <div className="text-white text-sm mb-2">
                                            {param.name}
                                          </div>
                                        )}
                                        <div className="flex justify-center">
                                          <div
                                            className={`rounded-xl border-4 p-1 ${
                                              isFullImageMode ? 'w-full max-w-4xl' : 'inline-flex max-w-full'
                                            }`}
                                            style={{
                                              borderColor: IMAGE_FRAME_COLOR,
                                              backgroundColor: 'rgba(143, 185, 150, 0.06)',
                                            }}
                                          >
                                            <img
                                              src={imageSrc}
                                              alt={param.name}
                                              className={`mx-auto ${
                                                isFullImageMode ? 'w-full max-w-4xl object-contain' : 'max-w-full max-h-96 object-contain'
                                              }`}
                                            />
                                          </div>
                                        </div>
                                      </td>
                                    </tr>
                                  );

                                  if (isReadOnlyParam(param) || !imageParamExpectsValueField(param)) {
                                    return imageRow;
                                  }

                                  return (
                                    <React.Fragment key={compositeKey}>
                                      {imageRow}
                                      <TableRowInput
                                        paramName={param.name}
                                        value={paramValues[compositeKey] ?? ''}
                                        value2={param.hasVal2 ? (paramValues2[compositeKey] ?? '') : ''}
                                        hasVal2={Boolean(param.hasVal2)}
                                        onChange={(nextValue, selectedId) => handleParamChange(compositeKey, nextValue, selectedId)}
                                        onChange2={param.hasVal2
                                          ? (next) => handleParamValue2Change(compositeKey, next)
                                          : undefined}
                                        onCommit={() => commitParamChange(compositeKey)}
                                        onCreateOption={() => handleCreateParamOption(block.id, param)}
                                        standardValues={getStandardValuesForParam(param, block.id)}
                                        typeData={getParamTypeData(param)}
                                        displayMode={param.displayMode}
                                        placeholder={getDistanceFieldPlaceholder(param)}
                                        canCreateOption={param.canCreateOption}
                                        isCreatingOption={savingOptionKey === compositeKey}
                                      />
                                    </React.Fragment>
                                  );
                                }

                                if (isReadOnlyParam(param)) {
                                  return (
                                    <ReadOnlyTableRow
                                      key={compositeKey}
                                      param={param}
                                      value={getReadOnlyParamDisplay(param, compositeKey, paramValues, paramValues2)}
                                    />
                                  );
                                }

                                return (
                                  <TableRowInput
                                    key={compositeKey}
                                    paramName={param.name}
                                    value={paramValues[compositeKey] ?? ''}
                                    value2={param.hasVal2 ? (paramValues2[compositeKey] ?? '') : ''}
                                    hasVal2={Boolean(param.hasVal2)}
                                    onChange={(nextValue, selectedId) => handleParamChange(compositeKey, nextValue, selectedId)}
                                    onChange2={param.hasVal2
                                      ? (next) => handleParamValue2Change(compositeKey, next)
                                      : undefined}
                                    onCommit={() => commitParamChange(compositeKey)}
                                    onCreateOption={() => handleCreateParamOption(block.id, param)}
                                    standardValues={getStandardValuesForParam(param, block.id)}
                                    typeData={getParamTypeData(param)}
                                    displayMode={param.displayMode}
                                    placeholder={getDistanceFieldPlaceholder(param)}
                                    canCreateOption={param.canCreateOption}
                                    isCreatingOption={savingOptionKey === compositeKey}
                                  />
                                );
                              })}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <p className={`text-[#646C89] text-center py-4 ${hasOperationRows ? 'hidden' : ''}`}>Нет параметров в этом блоке</p>
                      )}

                      {hasOperationRows && (
                        <div className={hasRegularParams ? 'mt-4' : ''}>
                          <OperationsTable block={block} />
                        </div>
                      )}

                      {(customFields[block.id] || []).length > 0 && (
                        <div className="mt-4 border-t border-[#646C89]/30 pt-4">
                          <p className="text-xs text-[#646C89] mb-2">Дополнительные поля:</p>
                          <div className="space-y-2">
                            {customFields[block.id].map((field) => (
                              <div key={field.id} className="flex gap-2 items-start">
                                <input
                                  type="text"
                                  value={field.name}
                                  onChange={(event) => updateCustomField(block.id, field.id, 'name', event.target.value)}
                                  placeholder="Название поля"
                                  className="flex-1 bg-[#0C1515] border border-[#646C89]/50 rounded px-3 py-1.5 text-white text-sm placeholder-[#646C89] focus:outline-none focus:border-[#D97B54]"
                                />
                                <input
                                  type="text"
                                  value={field.value}
                                  onChange={(event) => updateCustomField(block.id, field.id, 'value', event.target.value)}
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

                      {(uploadedImages[block.id] || []).length > 0 && (
                        <div className="mt-4 border-t border-[#646C89]/30 pt-4">
                          <p className="text-xs text-[#646C89] mb-2">Загруженные изображения:</p>
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                            {uploadedImages[block.id].map((image) => (
                              <div key={image.id} className="relative group">
                                <img
                                  src={image.preview}
                                  alt={image.name}
                                  className="w-full h-32 object-cover rounded-lg border-4"
                                  style={{ borderColor: IMAGE_FRAME_COLOR }}
                                />
                                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                                  <button
                                    type="button"
                                    onClick={() => deleteImage(block.id, image.id)}
                                    className="p-2 bg-red-500 hover:bg-red-600 rounded-full text-white transition-colors"
                                    title="Удалить изображение"
                                  >
                                    <X size={16} />
                                  </button>
                                </div>
                                <p className="text-xs text-[#646C89] mt-1 truncate" title={image.name}>
                                  {image.name}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="mt-4 flex flex-wrap gap-2">
                        <button
                          type="button"
                          onClick={(event) => {
                            event.stopPropagation();
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
                            onChange={(event) => handleImageUpload(block.id, event)}
                            className="hidden"
                          />
                        </label>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}

            <div className="pt-4 flex flex-col gap-3 md:flex-row">
              <button
                type="button"
                onClick={handleExport}
                disabled={isExporting || loadingBlocks}
                className={`
                  w-full md:flex-1 flex items-center justify-center gap-3
                  py-4 rounded-xl font-semibold text-lg
                  transition-all border
                  ${!isExporting && !loadingBlocks
                    ? 'border-[#8FB996]/40 bg-[#8FB996]/10 text-white hover:bg-[#8FB996]/18 hover:border-[#8FB996]/60'
                    : 'border-[#646C89]/30 text-[#646C89] bg-[#646C89]/15 cursor-not-allowed'
                  }
                `}
              >
                {isExporting ? (
                  <>
                    <Loader2 size={22} className="animate-spin" />
                    Подготовка документа...
                  </>
                ) : (
                  <>
                    <Download size={22} />
                    Скачать Word
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={!isFormValid() || isSubmitting}
                className={`
                  w-full md:flex-1 flex items-center justify-center gap-3
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
          </>
        )}
      </div>
    </div>
  );
};

export default TechCardForm;
