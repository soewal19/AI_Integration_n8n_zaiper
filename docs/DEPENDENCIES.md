# Зависимости и установка

## Runtime
Проект работает на стандартной библиотеке Python 3.10+ и не требует сторонних зависимостей для базового режима:
- HTTP: urllib.request
- БД: sqlite3
- Логи: logging

## Опционально
- Pydantic‑модели: `pydantic`
- Асинхронный HTTP: `httpx`
- Airflow (для запуска DAG): `apache-airflow==2.8.*` (ставится в окружении Airflow)
- Telegram‑клиент (если предпочитаете библиотеку): `python-telegram-bot`

## Dev‑инструменты
Файл: `requirements-dev.txt`
```
ruff
mypy
# pydantic
# httpx
# apache-airflow==2.8.*
# python-telegram-bot
```

Установка:
```bash
python -m pip install -r requirements-dev.txt
```

Проверка стиля и типов:
```bash
ruff check .
mypy .
```

Примечания:
- В CI GitHub Actions уже настроен запуск `ruff` и `mypy` (мягкий режим).
- Airflow зависимости устанавливайте в целевом окружении оркестратора (Docker/Composer), а не в локальном рантайме сервиса.

