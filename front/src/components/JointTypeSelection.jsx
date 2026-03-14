import React from 'react';
import { ArrowLeft, Link2 } from 'lucide-react';

// Выбор типа соединения (зависит от выбранного объекта)
const JointTypeSelection = ({ objectType, objectName, jointTypes, onSelect, onBack }) => {
  // Используем переданное имя объекта, или определяем по ID для обратной совместимости
  const displayName = objectName || (objectType === 'plate' ? 'Пластина' : objectType === 'pipe' ? 'Труба' : `Объект ${objectType}`);

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
        <div className="inline-block bg-[#0084FF]/20 text-[#0084FF] px-4 py-2 rounded-full text-sm mb-4">
          Объект: {displayName}
        </div>
        <h2 className="text-2xl font-bold text-white mb-3">
          Выберите тип сварного соединения
        </h2>
        <p className="text-[#646C89]">
          Доступные типы соединений для выбранного объекта
        </p>
      </div>

      <div className={`grid grid-cols-1 ${jointTypes.length > 1 ? 'md:grid-cols-2' : 'max-w-md mx-auto'} gap-6`}>
        {jointTypes.map((joint) => (
          <button
            key={joint.id}
            onClick={() => onSelect(joint.id)}
            className="
              bg-[#21262F] 
              border-2 border-[#646C89]/30
              hover:border-[#FFFB78]
              rounded-2xl 
              p-8
              text-center
              transition-all
              hover:shadow-lg hover:shadow-[#FFFB78]/10
              hover:scale-[1.02]
              group
            "
          >
            <div className="text-[#FFFB78] mb-4 flex justify-center group-hover:scale-110 transition-transform">
              <Link2 size={48} />
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">
              {joint.name}
            </h3>
            <p className="text-[#646C89]">
              {joint.description}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default JointTypeSelection;
