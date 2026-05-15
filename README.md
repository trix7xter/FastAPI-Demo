# FastAPI Demo

Демо-проект на FastAPI: бронирование отелей. Учебный пример с реальной БД (PostgreSQL), миграциями (Alembic) и асинхронным SQLAlchemy.

## Стек

- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.x (async)** — ORM, драйвер `asyncpg`
- **Alembic** — миграции (через синхронный `psycopg2`)
- **Pydantic v2 / pydantic-settings** — настройки и валидация
- **PostgreSQL** — БД

## Структура

```text
app/
├── config.py            # настройки из .env (BaseSettings)
├── database.py          # async engine + Base
├── main.py              # FastAPI app, эндпоинты
├── migrations/          # Alembic
│   ├── env.py
│   └── versions/
├── hotels/models.py     # модель Hotels
├── rooms/models.py      # модель Rooms
├── users/models.py      # модель Users
└── booking/models.py    # модель Bookings
alembic.ini
test_data.sql            # сидовые данные
.env                     # креды БД (не коммитится)
```

## Установка

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi "uvicorn[standard]" sqlalchemy asyncpg psycopg2-binary \
            alembic pydantic-settings greenlet
```

## Настройка `.env`

Создай в корне файл `.env`:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=
DB_NAME=postgres
```

## Миграции

```bash
# применить все миграции
alembic upgrade head

# сгенерировать новую миграцию по изменениям моделей
alembic revision --autogenerate -m "описание"
```

## Тестовые данные

```bash
psql -d postgres -f test_data.sql
```

Залит набор отелей, комнат, пользователей и бронирований для проверки.

## Запуск

```bash
uvicorn app.main:app --reload
```

- Swagger UI — <http://127.0.0.1:8000/docs>
- ReDoc — <http://127.0.0.1:8000/redoc>

## Модели

- **Hotels** — отели (название, локация, услуги JSON, кол-во номеров).
- **Rooms** — номера, FK → `hotels.id`.
- **Users** — пользователи (email, hashed_password).
- **Bookings** — бронирования, FK → `rooms.id`, `users.id`. Колонки `total_cost` и `total_days` вычисляются на стороне БД (`GENERATED ... STORED`).
