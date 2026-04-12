import React, { useState } from 'react';
import StartScreen from './components/StartScreen';
import TechCardForm from './components/TechCardForm';

function App() {
  const [showForm, setShowForm] = useState(false);
  const [initialSavedCard, setInitialSavedCard] = useState(null);

  const handleCreateNew = () => {
    setInitialSavedCard(null);
    setShowForm(true);
  };

  const handleOpenExisting = (savedCard) => {
    setInitialSavedCard(savedCard);
    setShowForm(true);
  };

  const handleBackToStart = () => setShowForm(false);

  return (
    <div className="nk-app min-h-screen bg-[#0C1515] text-white flex flex-col">
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
      <main className="flex flex-1">
        <div className="container mx-auto flex w-full max-w-6xl flex-1 flex-col px-4 py-8 md:px-8">
          {!showForm ? (
            <StartScreen
              onCreateNew={handleCreateNew}
              onOpenExisting={handleOpenExisting}
            />
          ) : (
            <TechCardForm
              key={initialSavedCard?.id ? `saved-${initialSavedCard.id}` : 'new-tech-card'}
              initialSavedCard={initialSavedCard}
            />
          )}
        </div>
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
