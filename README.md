# FastAPI Demo

Демо-проект на FastAPI: бронирование отелей. Учебный пример с реальной БД (PostgreSQL), миграциями (Alembic) и асинхронным SQLAlchemy.

## Стек

- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.x (async)** — ORM, драйвер `asyncpg`
- **Alembic** — миграции (через синхронный `psycopg2`)
- **Pydantic v2 / pydantic-settings** — настройки и валидация
- **PostgreSQL** — БД
- **python-jose** — JWT
- **passlib + bcrypt** — хэширование паролей

## Структура

```text
app/
├── config.py             # настройки из .env (BaseSettings)
├── database.py           # async engine + Base
├── exceptions.py         # кастомные HTTP-исключения (BookingException и наследники)
├── main.py               # FastAPI app, эндпоинты
├── dao/
│   └── base.py           # BaseDAO[Model] — generic CRUD
├── migrations/           # Alembic
│   ├── env.py
│   └── versions/
├── hotels/models.py      # модель Hotels
├── rooms/models.py       # модель Rooms
├── users/
│   ├── models.py         # модель Users
│   ├── schemas.py        # SUserAuth
│   ├── dao.py            # UsersDao
│   ├── auth.py           # хэш паролей, JWT, authenticate_user
│   ├── dependencies.py   # get_token / get_current_user / get_current_admin_user
│   └── router.py         # /auth/register, /login, /logout, /me, /all
└── booking/
    ├── models.py         # модель Bookings
    ├── schemas.py        # SBooking
    ├── dao.py            # BookingDAO
    └── router.py         # /bookings
alembic.ini
test_data.sql             # сидовые данные
.env                      # креды БД и JWT (не коммитится)
```

## Установка

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi "uvicorn[standard]" sqlalchemy asyncpg psycopg2-binary \
            alembic 'pydantic[email]' pydantic-settings greenlet \
            'python-jose[cryptography]' 'passlib[bcrypt]' 'bcrypt==4.0.1'
```

> `bcrypt` пинится на `4.0.1` из-за известной несовместимости `passlib 1.7.4` с `bcrypt>=4.1` (валится с `AttributeError: __about__`).

## Настройка `.env`

Создай в корне файл `.env`:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=
DB_NAME=postgres

SECRET_KEY=your-very-secret-key
ALGORITHM=HS256
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

## Аутентификация

JWT в httpOnly-cookie + bcrypt-хэш паролей. Кастомные исключения вынесены в `app/exceptions.py` (базовый `BookingException`, наследники — `UserAlreadyExistsException`, `IncorrectEmailOrPasswordException`, `TokenExpiredException` и т.д.).

### Эндпоинты

| Метод | Путь              | Описание                                  |
|-------|-------------------|-------------------------------------------|
| POST  | `/auth/register`  | Регистрация — 201 / 409 если email занят  |
| POST  | `/auth/login`     | Логин — выдаёт JWT в cookie               |
| POST  | `/auth/logout`    | Сброс cookie                              |
| GET   | `/auth/me`        | Текущий пользователь                      |
| GET   | `/auth/all`       | Все пользователи (только админ)           |
| GET   | `/bookings`       | Список бронирований текущего пользователя |

### Быстрая проверка через curl

```bash
# регистрация
curl -i -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"12345"}'

# логин (-c сохранит cookie)
curl -i -X POST http://127.0.0.1:8000/auth/login \
  -c cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"12345"}'

# защищённый эндпоинт (-b пошлёт cookie)
curl -i http://127.0.0.1:8000/bookings -b cookies.txt
```
