import React from 'react';
import { Square, Circle, ArrowLeft } from 'lucide-react';

// Выбор типа объекта (Пластина или Труба)
const ObjectSelection = ({ objectTypes, onSelect, onBack }) => {
  const getIcon = (iconName) => {
    switch (iconName) {
      case 'square':
        return <Square size={64} />;
      case 'circle':
        return <Circle size={64} />;
      default:
        return <Square size={64} />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-[#646C89] hover:text-white mb-8 transition-colors"
      >
        <ArrowLeft size={20} />
        Назад
      </button>

      <div className="text-center mb-10">
        <h2 className="text-2xl font-bold text-white mb-3">
          Выберите тип объекта контроля
        </h2>
        <p className="text-[#646C89]">
          От выбора зависит набор параметров и тип сварного соединения
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {objectTypes.map((obj) => (
          <button
            key={obj.id}
            onClick={() => onSelect(obj.id)}
            className="
              bg-[#21262F] 
              border-2 border-[#646C89]/30
              hover:border-[#0084FF]
              rounded-2xl 
              p-8
              text-center
              transition-all
              hover:shadow-lg hover:shadow-[#0084FF]/10
              hover:scale-[1.02]
              group
            "
          >
            <div className="text-[#0084FF] mb-4 flex justify-center group-hover:scale-110 transition-transform">
              {getIcon(obj.icon)}
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">
              {obj.name}
            </h3>
            <p className="text-[#646C89]">
              {obj.description}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ObjectSelection;
