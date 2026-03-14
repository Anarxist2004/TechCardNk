import React from 'react';
import { Plus, FileText } from 'lucide-react';

// Начальный экран с кнопкой создания новой карты
const StartScreen = ({ onCreateNew }) => {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center">
      <div className="text-center mb-12">
        <FileText size={80} className="mx-auto mb-6 text-[#0084FF]" />
        <h2 className="text-3xl font-bold text-white mb-4">
          Конструктор технологических карт
        </h2>
        <p className="text-[#646C89] text-lg max-w-md mx-auto">
          Создавайте технологические карты для неразрушающего контроля сварных соединений
        </p>
      </div>

      <button
        onClick={onCreateNew}
        className="
          flex items-center gap-3
          bg-[#0084FF] hover:bg-[#0084FF]/80
          text-white
          px-8 py-5
          rounded-xl
          text-xl font-semibold
          transition-all
          shadow-lg hover:shadow-[#0084FF]/30
          hover:scale-105
        "
      >
        <Plus size={28} />
        Создать новую тех карту
      </button>
    </div>
  );
};

export default StartScreen;
