# Единый сервис НК

Запуск из папки `portal`:

```powershell
python -m uvicorn main:app --reload --port 8000
```

После запуска откройте `http://127.0.0.1:8000/`.

- Авторизация хранит пользователей и cookie-сессии в PostgreSQL, в таблицах `public.users` и `public.sessions`.
- DSN берётся из `AUTH_DB_DSN`, если переменная задана; иначе используется основная база `victor_2`.
- SQL для создания таблиц находится в `portal/sql/auth_postgres.sql`.
- `/tech-cards/` открывает модуль технологических карт.
- `/expert-analysis/` открывает модуль экспертной оценки.
