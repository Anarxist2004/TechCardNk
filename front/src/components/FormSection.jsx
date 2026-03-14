import React from 'react';
import FormField from './FormField';

// Компонент для рендеринга секции формы
const FormSection = ({ section, values, onChange }) => {
  const { id, title, fields } = section;

  return (
    <div className="bg-[#21262F] rounded-lg p-6 shadow-xl">
      <h2 className="text-xl font-semibold text-[#FFFB78] mb-6 border-b border-[#646C89] pb-3">
        {title}
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {fields.map((field) => (
          <FormField
            key={field.id}
            field={field}
            value={values[field.id]}
            onChange={onChange}
          />
        ))}
      </div>
    </div>
  );
};

export default FormSection;
