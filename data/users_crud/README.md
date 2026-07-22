# Users CRUD API

FastAPI-проект, предоставляющий REST API для управления пользователями (CRUD).

## Стек технологий

- **Python 3.14+**
- **FastAPI** — веб-фреймворк
- **SQLAlchemy Core** — асинхронный доступ к БД
- **SQLite** — база данных
- **Alembic** — миграции БД
- **Pydantic** — валидация данных
- **uv** — управление зависимостями и окружением
- **ruff** — линтер
- **pytest + pytest-asyncio + httpx** — тестирование

## Структура проекта

```
users_crud/
├── app/
│   ├── main.py                  # Точка входа FastAPI
│   ├── config.py                # Настройки (URL БД)
│   ├── database.py              # Асинхронный движок и сессии SQLAlchemy
│   ├── models/
│   │   └── __init__.py          # Схема таблицы (SQLAlchemy Core)
│   ├── repositories/
│   │   └── user_repository.py   # Слой доступа к БД (CRUD-операции)
│   ├── services/
│   │   └── user_service.py      # Бизнес-логика
│   ├── schemas/
│   │   └── user_schemas.py      # Pydantic-схемы (запрос/ответ)
│   └── routers/
│       └── user_router.py       # REST-эндпоинты
├── tests/
│   └── test_users.py            # Тесты на веб-ручки
├── alembic/                     # Миграции Alembic
├── alembic.ini
├── pyproject.toml
└── README.md
```

## Установка и запуск

### 1. Установите зависимости

```bash
cd users_crud
uv sync
```

### 2. Примените миграции БД

```bash
uv run alembic upgrade head
```

### 3. Запустите сервер

```bash
uv run uvicorn app.main:app --reload --host=0.0.0.0
```

Сервер будет доступен по адресу `http://localhost:8000`.  
Интерактивная документация: `http://localhost:8000/docs`.

## API

### Создать пользователя

```
POST /users/
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com"
}
```

**Ответ:** `201 Created` — тело с данными созданного пользователя (включая `id`).

### Получить всех пользователей

```
GET /users/
```

**Ответ:** `200 OK` — массив пользователей.

### Получить пользователя по ID

```
GET /users/{user_id}
```

**Ответ:** `200 OK` — данные пользователя или `404 Not Found`.

### Обновить пользователя

```
PUT /users/{user_id}
Content-Type: application/json

{
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@example.com"
}
```

**Ответ:** `200 OK` — обновлённые данные или `404 Not Found`.

### Удалить пользователя

```
DELETE /users/{user_id}
```

**Ответ:** `204 No Content` или `404 Not Found`.

## Тестирование

Тесты используют отдельную тестовую БД `users_db_test.db`.

```bash
uv run pytest tests/ -v
```

## Линтинг

```bash
uv run ruff check .
```
