import React, { useState } from 'react';
import { FileText, FolderOpen, Loader2, Plus, RefreshCw } from 'lucide-react';

import api from '../services/api';

const formatSavedCardDate = (value) => {
  if (!value) {
    return 'Дата неизвестна';
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return String(value);
  }

  return parsed.toLocaleString('ru-RU');
};

const StartScreen = ({ onCreateNew, onOpenExisting }) => {
  const [showSavedCards, setShowSavedCards] = useState(false);
  const [savedCards, setSavedCards] = useState([]);
  const [isLoadingCards, setIsLoadingCards] = useState(false);
  const [loadCardsError, setLoadCardsError] = useState('');
  const [openingCardId, setOpeningCardId] = useState(null);

  const loadSavedCards = async () => {
    setIsLoadingCards(true);
    setLoadCardsError('');

    try {
      const cards = await api.listSavedTechCards();
      setSavedCards(cards);
    } catch (error) {
      console.error('Ошибка загрузки списка техкарт:', error);
      setLoadCardsError('Не удалось загрузить список сохранённых карт.');
    } finally {
      setIsLoadingCards(false);
    }
  };

  const handleOpenList = async () => {
    const nextShowState = !showSavedCards;
    setShowSavedCards(nextShowState);

    if (nextShowState) {
      await loadSavedCards();
    }
  };

  const handleOpenSavedCard = async (cardId) => {
    setOpeningCardId(cardId);

    try {
      const savedCard = await api.getSavedTechCard(cardId);
      onOpenExisting(savedCard);
    } catch (error) {
      console.error('Ошибка открытия сохранённой карты:', error);
      alert(`Не удалось открыть карту: ${error.message}`);
    } finally {
      setOpeningCardId(null);
    }
  };

  return (
    <div className="flex flex-1 flex-col items-center justify-center">
      <div className="text-center mb-12">
        <FileText size={80} className="mx-auto mb-6 text-[#0084FF]" />
        <h2 className="text-3xl font-bold text-white mb-4">
          Конструктор технологических карт
        </h2>
        <p className="text-[#646C89] text-lg max-w-md mx-auto">
          Создавайте технологические карты для неразрушающего контроля сварных соединений
        </p>
      </div>

      <div className="flex w-full max-w-3xl flex-col gap-4">
        <div className="grid gap-4 md:grid-cols-2">
          <button
            onClick={onCreateNew}
            className="
              flex items-center justify-center gap-3
              bg-[#0084FF] hover:bg-[#0084FF]/80
              text-white
              px-8 py-5
              rounded-xl
              text-xl font-semibold
              transition-all
              shadow-lg hover:shadow-[#0084FF]/30
              hover:scale-[1.01]
            "
          >
            <Plus size={28} />
            Создать технологическую карту
          </button>

          <button
            onClick={() => void handleOpenList()}
            className="
              flex items-center justify-center gap-3
              border border-[#646C89]/30 bg-[#21262F] hover:bg-[#21262F]/80
              text-white
              px-8 py-5
              rounded-xl
              text-xl font-semibold
              transition-all
            "
          >
            <FolderOpen size={28} />
            Открыть существующую
          </button>
        </div>

        {showSavedCards && (
          <div className="rounded-2xl border border-[#646C89]/30 bg-[#21262F] p-5">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-white">Сохранённые карты</h3>
                <p className="text-sm text-[#646C89]">
                  Выберите карту, чтобы открыть её с сохранёнными данными.
                </p>
              </div>

              <button
                type="button"
                onClick={() => void loadSavedCards()}
                disabled={isLoadingCards}
                className="flex items-center gap-2 rounded-lg border border-[#646C89]/30 px-3 py-2 text-sm text-[#646C89] hover:bg-[#646C89]/10 disabled:cursor-not-allowed"
              >
                {isLoadingCards ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
                Обновить
              </button>
            </div>

            {loadCardsError ? (
              <p className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                {loadCardsError}
              </p>
            ) : null}

            {!loadCardsError && isLoadingCards ? (
              <div className="flex items-center justify-center gap-3 py-8 text-[#646C89]">
                <Loader2 size={20} className="animate-spin" />
                Загрузка списка карт...
              </div>
            ) : null}

            {!loadCardsError && !isLoadingCards && savedCards.length === 0 ? (
              <p className="py-6 text-center text-[#646C89]">
                В базе пока нет сохранённых технологических карт.
              </p>
            ) : null}

            {!loadCardsError && !isLoadingCards && savedCards.length > 0 ? (
              <div className="space-y-3">
                {savedCards.map((card) => (
                  <button
                    key={card.id}
                    type="button"
                    onClick={() => void handleOpenSavedCard(card.id)}
                    disabled={openingCardId === card.id}
                    className="flex w-full items-center justify-between rounded-xl border border-[#646C89]/20 bg-[#0C1515]/50 px-4 py-4 text-left transition-colors hover:border-[#D97B54]/40 hover:bg-[#0C1515]"
                  >
                    <div>
                      <div className="text-base font-semibold text-white">
                        {card.name || `Техкарта #${card.id}`}
                      </div>
                      <div className="mt-1 text-sm text-[#646C89]">
                        Обновлена: {formatSavedCardDate(card.updatedAt || card.createdAt)}
                      </div>
                    </div>

                    {openingCardId === card.id ? (
                      <Loader2 size={18} className="animate-spin text-[#D97B54]" />
                    ) : (
                      <FolderOpen size={18} className="text-[#D97B54]" />
                    )}
                  </button>
                ))}
              </div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
};

export default StartScreen;
