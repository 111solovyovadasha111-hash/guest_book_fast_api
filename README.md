# Гостевая книга
Самостоятельный JSON API на FastAPI и SQLAlchemy.

## Виртуальное окружение и зависимости:
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Запуск

Сначала примените миграции Alembic:
```bash
python -m alembic upgrade head
```

Затем запустите сервер:

```bash
python -m uvicorn main:app --reload
```

## Тесты

```bash
python -m pytest -v 
```
