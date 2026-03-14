import React from 'react';

// Компонент для рендеринга отдельного поля формы
const FormField = ({ field, value, onChange }) => {
  const { id, label, type } = field;

  const handleChange = (e) => {
    onChange(id, e.target.value);
  };

  const inputClasses = `
    w-full 
    bg-[#21262F] 
    border border-[#646C89] 
    rounded-lg 
    px-4 py-3 
    text-white 
    placeholder-[#646C89]
    focus:outline-none 
    focus:border-[#0084FF]
    transition-colors
  `;

  return (
    <div className="flex flex-col gap-2">
      <label 
        htmlFor={id} 
        className="text-[#646C89] text-sm font-medium"
      >
        {id}. {label}
      </label>
      
      {type === 'textarea' ? (
        <textarea
          id={id}
          value={value || ''}
          onChange={handleChange}
          placeholder={`Введите ${label.toLowerCase()}`}
          rows={3}
          className={`${inputClasses} resize-none`}
        />
      ) : (
        <input
          id={id}
          type={type}
          value={value || ''}
          onChange={handleChange}
          placeholder={`Введите ${label.toLowerCase()}`}
          className={inputClasses}
        />
      )}
    </div>
  );
};

export default FormField;
