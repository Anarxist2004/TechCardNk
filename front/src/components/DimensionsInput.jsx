import React, { useState, useEffect } from 'react';
import { ArrowLeft, ArrowRight, Ruler, ChevronDown, Loader2 } from 'lucide-react';
import api from '../services/api';

// Ввод размеров контролируемого элемента с подгрузкой стандартных значений
const DimensionsInput = ({ objectType, objectName, jointType, jointName, dimensionFields, values, onChange, onNext, onBack }) => {
  // Состояние для стандартных значений каждого параметра
  const [standardValues, setStandardValues] = useState({});
  const [loadingValues, setLoadingValues] = useState({});
  const [openDropdown, setOpenDropdown] = useState(null);

  // Загрузка стандартных значений при монтировании или изменении полей
  useEffect(() => {
    const loadStandardValues = async () => {
      if (!dimensionFields || dimensionFields.length === 0 || !objectType) return;

      const newStandardValues = {};
      const newLoadingValues = {};

      // Отмечаем все поля как загружающиеся
      dimensionFields.forEach(field => {
        newLoadingValues[field.id] = true;
      });
      setLoadingValues(newLoadingValues);

      // Загружаем значения для каждого параметра
      for (const field of dimensionFields) {
        try {
          // API возвращает { available: { paramId: [value1, value2, ...] } }
          const rawData = await api.raw.getParamValues(parseInt(objectType), parseInt(field.id));
          
          if (rawData && rawData.available && rawData.available[field.id]) {
            newStandardValues[field.id] = rawData.available[field.id];
          } else {
            newStandardValues[field.id] = [];
          }
        } catch (error) {
          console.error(`Ошибка загрузки значений для ${field.id}:`, error);
          newStandardValues[field.id] = [];
        }
        
        newLoadingValues[field.id] = false;
        setLoadingValues({ ...newLoadingValues });
      }

      setStandardValues(newStandardValues);
    };

    loadStandardValues();
  }, [dimensionFields, objectType]);

  const handleChange = (fieldId, value) => {
    onChange(fieldId, value);
  };

  const handleSelectStandard = (fieldId, value) => {
    onChange(fieldId, value.toString());
    setOpenDropdown(null);
  };

  const toggleDropdown = (fieldId) => {
    setOpenDropdown(openDropdown === fieldId ? null : fieldId);
  };

  const isValid = () => {
    return dimensionFields
      .filter(f => f.required)
      .every(f => values[f.id] && values[f.id].toString().trim() !== '');
  };

  // Закрытие dropdown при клике вне
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (!e.target.closest('.dropdown-container')) {
        setOpenDropdown(null);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  // Используем переданные имена или fallback
  const displayObjectName = objectName || `Объект ${objectType}`;
  const displayJointName = jointName || `Элемент ${jointType}`;

  return (
    <div className="max-w-3xl mx-auto">
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-[#646C89] hover:text-white mb-8 transition-colors"
      >
        <ArrowLeft size={20} />
        Назад
      </button>

      <div className="text-center mb-10">
        <div className="flex justify-center gap-2 mb-4">
          <span className="inline-block bg-[#0084FF]/20 text-[#0084FF] px-4 py-2 rounded-full text-sm">
            {displayObjectName}
          </span>
          <span className="inline-block bg-[#FFFB78]/20 text-[#FFFB78] px-4 py-2 rounded-full text-sm">
            {displayJointName}
          </span>
        </div>
        <h2 className="text-2xl font-bold text-white mb-3">
          Размеры контролируемого элемента
        </h2>
        <p className="text-[#646C89]">
          Выберите стандартное значение или введите своё
        </p>
      </div>

      <div className="bg-[#21262F] rounded-2xl p-6 mb-8">
        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[#646C89]/30">
          <Ruler className="text-[#0084FF]" size={24} />
          <h3 className="text-lg font-semibold text-white">
            Параметры размеров
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {dimensionFields.map((field) => (
            <div key={field.id} className="flex flex-col gap-2 dropdown-container relative">
              <label 
                htmlFor={field.id}
                className="text-[#646C89] text-sm font-medium"
              >
                {field.label}
                {field.required && <span className="text-[#FFFB78] ml-1">*</span>}
              </label>
              
              <div className="relative">
                <input
                  id={field.id}
                  type="text"
                  value={values[field.id] || ''}
                  onChange={(e) => handleChange(field.id, e.target.value)}
                  placeholder={`Введите значение`}
                  className="
                    w-full
                    bg-[#0C1515]
                    border border-[#646C89]
                    rounded-lg
                    px-4 py-3
                    pr-10
                    text-white
                    placeholder-[#646C89]
                    focus:outline-none
                    focus:border-[#0084FF]
                    transition-colors
                  "
                />
                
                {/* Кнопка открытия dropdown со стандартными значениями */}
                {loadingValues[field.id] ? (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    <Loader2 size={18} className="animate-spin text-[#646C89]" />
                  </div>
                ) : standardValues[field.id] && standardValues[field.id].length > 0 ? (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleDropdown(field.id);
                    }}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[#646C89] hover:text-[#0084FF] transition-colors"
                  >
                    <ChevronDown 
                      size={18} 
                      className={`transition-transform ${openDropdown === field.id ? 'rotate-180' : ''}`}
                    />
                  </button>
                ) : null}

                {/* Dropdown со стандартными значениями */}
                {openDropdown === field.id && standardValues[field.id] && standardValues[field.id].length > 0 && (
                  <div className="
                    absolute top-full left-0 right-0 mt-1
                    bg-[#0C1515]
                    border border-[#646C89]
                    rounded-lg
                    shadow-lg
                    z-50
                    max-h-48
                    overflow-y-auto
                  ">
                    <div className="p-2 border-b border-[#646C89]/30">
                      <span className="text-xs text-[#646C89]">Стандартные значения:</span>
                    </div>
                    {standardValues[field.id].map((val, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => handleSelectStandard(field.id, val)}
                        className="
                          w-full text-left
                          px-4 py-2
                          text-white
                          hover:bg-[#0084FF]/20
                          transition-colors
                        "
                      >
                        {val}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Подсказка о количестве стандартных значений */}
              {!loadingValues[field.id] && standardValues[field.id] && standardValues[field.id].length > 0 && (
                <span className="text-xs text-[#646C89]">
                  {standardValues[field.id].length} стандартных значений доступно
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={onNext}
          disabled={!isValid()}
          className={`
            flex items-center gap-2
            px-6 py-3
            rounded-lg
            font-semibold
            transition-all
            ${isValid()
              ? 'bg-[#0084FF] hover:bg-[#0084FF]/80 text-white'
              : 'bg-[#646C89]/30 text-[#646C89] cursor-not-allowed'
            }
          `}
        >
          Продолжить
          <ArrowRight size={20} />
        </button>
      </div>
    </div>
  );
};

export default DimensionsInput;
