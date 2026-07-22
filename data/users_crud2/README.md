# Users CRUD API

REST API для управления пользователями, построенный на **FastAPI** с использованием **SQLAlchemy Core** и **SQLite**.

## Стек технологий

- **FastAPI** — веб-фреймворк
- **SQLAlchemy Core** — работа с БД (без ORM)
- **aiosqlite** — асинхронный драйвер SQLite
- **Alembic** — миграции базы данных
- **Pydantic** — валидация данных
- **Ruff** — линтер
- **pytest + httpx** — тестирование

## Структура проекта

```
users_crud2/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Точка входа FastAPI
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py            # Конфигурация (пути к БД)
│   ├── db/
│   │   ├── __init__.py
│   │   └── models.py            # SQLAlchemy Core таблицы
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── user_repository.py   # Слой доступа к данным
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py      # Бизнес-логика
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py              # Pydantic-схемы
│   └── routers/
│       ├── __init__.py
│       └── users.py             # REST-ручки
├── tests/
│   ├── __init__.py
│   └── test_users.py            # Тесты на веб-ручки
├── alembic/                     # Миграции Alembic
├── alembic.ini
├── pyproject.toml
└── README.md
```

## Модель данных

Таблица `users`:

| Поле        | Тип          | Ограничения              |
|-------------|-------------|--------------------------|
| id          | INTEGER     | PRIMARY KEY, AUTOINCREMENT |
| first_name  | VARCHAR(200)| NOT NULL                 |
| last_name   | VARCHAR(200)| NOT NULL                 |
| email       | VARCHAR(255)| NOT NULL                 |

## API Endpoints

| Метод   | Путь               | Описание              | Статус-код |
|---------|-------------------|-----------------------|------------|
| POST    | /api/v1/users     | Создать пользователя  | 201        |
| GET     | /api/v1/users     | Получить всех         | 200        |
| GET     | /api/v1/users/{id}| Получить по ID        | 200/404    |
| PUT     | /api/v1/users/{id}| Обновить пользователя | 200/404    |
| DELETE  | /api/v1/users/{id}| Удалить пользователя  | 204/404    |

## Установка и запуск

### 1. Установка зависимостей

```bash
uv sync
```

### 2. Применение миграций

```bash
uv run alembic upgrade head
```

### 3. Запуск сервера

```bash
uv run uvicorn app.main:app --reload
```

Сервер будет доступен по адресу: `http://localhost:8000`

Документация API: `http://localhost:8000/docs`

## Тестирование

Тесты используют отдельную тестовую БД `users_db_test.sqlite`:

```bash
uv run pytest tests/ -v
```

## Линтинг

```bash
uv run ruff check app/ tests/
```

## Создание миграций

```bash
# Создать новую миграцию
uv run alembic revision --autogenerate -m "описание миграции"

# Применить миграции
uv run alembic upgrade head

# Откатить миграции
uv run alembic downgrade -1
```
