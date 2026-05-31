# Единый сервис НК

Запуск из папки `portal`:

```powershell
python -m uvicorn main:app --reload --port 8000
```

После запуска откройте `http://127.0.0.1:8000/`.

- `portal/auth.sqlite3` хранит пользователей и cookie-сессии.
- `/tech-cards/` открывает модуль технологических карт.
- `/expert-analysis/` открывает модуль экспертной оценки.
