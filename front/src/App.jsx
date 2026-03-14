import React, { useState } from 'react';
import { Plus } from 'lucide-react';
import StartScreen from './components/StartScreen';
import TechCardForm from './components/TechCardForm';

function App() {
  const [showForm, setShowForm] = useState(false);

  const handleCreateNew = () => {
    setShowForm(true);
  };

  const handleBackToStart = () => {
    setShowForm(false);
  };

  return (
    <div className="min-h-screen bg-[#0C1515] text-white">
      {/* Шапка */}
      <header className="bg-[#21262F] border-b border-[#646C89]/30 py-6 px-8">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div>
            <h1 
              onClick={handleBackToStart}
              className="text-3xl font-bold text-[#0084FF] cursor-pointer hover:opacity-80 transition-opacity"
            >
              Конструктор технологических карт
            </h1>
            <p className="text-[#646C89] mt-2">
              Неразрушающий контроль сварных соединений (НК)
            </p>
          </div>
          
          {showForm && (
            <button
              onClick={handleBackToStart}
              className="text-[#646C89] hover:text-white text-sm transition-colors"
            >
              ← На главную
            </button>
          )}
        </div>
      </header>

      {/* Основной контент */}
      <main className="container mx-auto px-4 md:px-8 py-8 max-w-6xl">
        {!showForm ? (
          <StartScreen onCreateNew={handleCreateNew} />
        ) : (
          <TechCardForm />
        )}
      </main>

      {/* Футер */}
      <footer className="bg-[#21262F] border-t border-[#646C89]/30 py-4 px-8 text-center">
        <p className="text-[#646C89] text-sm">
          Конструктор технологических карт © 2026
        </p>
      </footer>
    </div>
  );
}

export default App;
