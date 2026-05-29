# FastAPI Demo

Демо-проект на FastAPI: бронирование отелей. Учебный пример с реальной БД (PostgreSQL), миграциями (Alembic) и асинхронным SQLAlchemy.

## Стек

- **FastAPI** — веб-фреймворк
- **fastapi-versioning** — версионирование API (`/v1`, `/latest`, отдельные docs на версию)
- **SQLAlchemy 2.x (async)** — ORM, драйвер `asyncpg`
- **Alembic** — миграции (через синхронный `psycopg2`)
- **Pydantic v2 / pydantic-settings** — настройки и валидация
- **PostgreSQL** — БД
- **Redis** — брокер Celery и бэкенд кеша
- **Celery** — фоновые задачи (отправка писем, ресайз изображений)
- **fastapi-cache2** — кеширование ответов в Redis
- **SQLAdmin** — админка поверх SQLAlchemy
- **Jinja2** — серверный рендеринг страниц
- **Pillow** — обработка изображений
- **python-jose** — JWT
- **passlib + bcrypt** — хэширование паролей
- **pytest + pytest-asyncio + httpx** — автотесты (unit + integration на отдельной TEST-БД)

## Структура

```text
app/
├── config.py             # настройки из .env (BaseSettings)
├── database.py           # async engine + Base
├── exceptions.py         # кастомные HTTP-исключения
├── main.py               # FastAPI app, подключение роутеров, обёртка VersionedFastAPI (/v1)
├── dao/
│   └── base.py           # BaseDAO[Model] — generic CRUD (find_by_id, find_all, add, delete)
├── migrations/           # Alembic
│   ├── env.py
│   └── versions/
├── hotels/
│   ├── models.py         # модель Hotels
│   ├── schemas.py        # SHotel, SHotelInfo
│   ├── dao.py            # HotelDAO.find_all(location, date_from, date_to)
│   ├── router.py         # /hotels/{location}, /hotels/id/{id}
│   └── rooms/
│       ├── models.py     # модель Rooms
│       ├── schemas.py    # SRoom, SRoomInfo
│       ├── dao.py        # RoomDAO.find_all(hotel_id, date_from, date_to)
│       └── router.py     # /hotels/{hotel_id}/rooms (присоединён к router отелей)
├── users/
│   ├── models.py         # модель Users
│   ├── schemas.py        # SUserAuth
│   ├── dao.py            # UsersDao
│   ├── auth.py           # хэш паролей, JWT, authenticate_user
│   ├── dependencies.py   # get_token / get_current_user / get_current_admin_user
│   └── router.py         # /auth/register, /login, /logout, /me, /all
├── bookings/
│   ├── models.py         # модель Bookings
│   ├── schemas.py        # SBooking, SBookingInfo
│   ├── dao.py            # BookingDAO (add с проверкой свободных номеров, find_all с join к Rooms)
│   └── router.py         # /bookings, после успешной брони ставит celery-таск на email
├── admin/
│   └── views.py          # UserAdmin / BookingsAdmin для sqladmin
├── pages/
│   └── router.py         # /pages/hotels — рендер страницы через Jinja2
├── images/
│   └── router.py         # /images/hotels — загрузка картинки + celery-таск ресайза
├── tasks/
│   ├── celery.py         # celery-приложение, брокер на Redis
│   ├── tasks.py          # process_pic, send_booking_confirmation_email
│   └── email_templates.py
├── templates/
│   └── hotels.html       # Jinja-шаблон страницы списка отелей
├── static/
│   └── images/           # отдаётся через /static, сюда падают результаты ресайза
├── conftest.py           # выставляет MODE=TEST до импорта settings
└── tests/
    ├── conftest.py       # фикстуры: prepare_database, ac, authenticated_ac, session
    ├── mock_*.json       # сидовые данные для TEST-БД
    ├── unit_tests/       # быстрые DAO-тесты (без HTTP)
    └── integration_tests/ # HTTP-тесты через httpx.AsyncClient + ASGITransport
alembic.ini
pytest.ini                # pythonpath, asyncio_mode=auto, session-scope loop
create_admin.py           # одноразовое создание админ-пользователя
test_data.sql             # сидовые данные для DEV-БД
.env                      # креды БД, JWT, SMTP, Redis (не коммитится)
```

Модели описаны в типизированном стиле SQLAlchemy 2.0 (`Mapped` / `mapped_column`).
Роутер для `/hotels/{hotel_id}/rooms` не создаёт отдельный `APIRouter`, а импортирует существующий из `app/hotels/router.py` и добавляет эндпоинт к нему — поэтому в `main.py` подключается только `router_hotels`, а модуль `app.hotels.rooms.router` импортируется ради side-effect регистрации.

## Установка

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi "uvicorn[standard]" sqlalchemy asyncpg psycopg2-binary \
            alembic 'pydantic[email]' pydantic-settings greenlet \
            'python-jose[cryptography]' 'passlib[bcrypt]' 'bcrypt==4.0.1' \
            redis fastapi-cache2 celery sqladmin itsdangerous jinja2 pillow python-multipart \
            fastapi-versioning
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

MODE=DEV

TEST_DB_HOST=localhost
TEST_DB_PORT=5432
TEST_DB_USER=postgres
TEST_DB_PASS=
TEST_DB_NAME=test_booking_db

SECRET_KEY=your-very-secret-key
ALGORITHM=HS256

SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=you@example.com
SMTP_PASSWORD=app-password

REDIS_HOST=localhost
REDIS_PORT=6379
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

Нужны запущенные PostgreSQL и Redis. Самый простой вариант для Redis:

```bash
redis-server
```

Веб-приложение:

```bash
uvicorn app.main:app --reload
```

Celery-воркер (в отдельном терминале — нужен, чтобы реально отправлялись письма и ресайзились картинки):

```bash
celery -A app.tasks.celery:celery worker --loglevel=INFO
```

- Swagger UI (v1) — <http://127.0.0.1:8000/v1/docs>
- Корневой Swagger со ссылками на версии — <http://127.0.0.1:8000/docs>
- ReDoc — <http://127.0.0.1:8000/redoc>
- Админка SQLAdmin (без версии) — <http://127.0.0.1:8000/admin>
- Страница отелей (Jinja) — <http://127.0.0.1:8000/v1/pages/hotels?location=...&date_from=...&date_to=...>>

## Модели

- **Hotels** — отели (название, локация, услуги JSON, кол-во номеров).
- **Rooms** — номера, FK → `hotels.id`.
- **Users** — пользователи (email, hashed_password).
- **Bookings** — бронирования, FK → `rooms.id`, `users.id`. Колонки `total_cost` и `total_days` вычисляются на стороне БД (`GENERATED ... STORED`).

## Аутентификация

JWT в httpOnly-cookie + bcrypt-хэш паролей. Кастомные исключения вынесены в `app/exceptions.py` (базовый `BookingException`, наследники — `UserAlreadyExistsException`, `IncorrectEmailOrPasswordException`, `TokenExpiredException` и т.д.).

## Кеширование

`GET /v1/hotels/{location}` обёрнут `@cache(expire=30)` из `fastapi-cache2`. Бэкенд кеша — Redis, инициализируется в lifespan FastAPI (`RedisBackend` поверх `redis.asyncio`). lifespan передаётся в родительское `VersionedFastAPI`, поэтому кеш инициализируется один раз и доступен всем версиям.

## Фоновые задачи (Celery)

Celery-приложение — `app/tasks/celery.py`, брокер — Redis (`REDIS_HOST`/`REDIS_PORT`). Задачи:

- `send_booking_confirmation_email(booking, email_to)` — отправляет письмо через SMTP (`SMTP_HOST`/`SMTP_PORT`/`SMTP_USER`/`SMTP_PASSWORD`). Шаблон — `app/tasks/email_templates.py`. Ставится из `POST /v1/bookings` после успешной брони.
- `process_pic(path)` — открывает картинку через Pillow, сохраняет варианты `1000×500` и `200×100` в `app/static/images/`. Ставится из `POST /v1/images/hotels`.

## Админка

`SQLAdmin` подключается в `app/main.py`, вьюхи описаны в `app/admin/views.py`:

- `UserAdmin` — список юзеров, `hashed_password` скрыт в детальном виде, удаление запрещено (`can_delete = False`).
- `BookingsAdmin` — все колонки + связь с пользователем (`relationship` обоюдный: `Users.booking` ↔ `Bookings.user`).
- `HotelsAdmin` / `RoomsAdmin` — отели и номера со связями `Hotels.rooms`, `Rooms.hotel`, `Rooms.booking`.

Аутентификация поверх sqladmin реализована в `app/admin/auth.py` (`AdminAuth(AuthenticationBackend)`), переиспользует `authenticate_user` и `get_current_user` из `app/users`. Токен кладётся в сессию sqladmin (`secret_key=settings.SECRET_KEY`).

Создать админ-пользователя можно одноразовым скриптом:

```bash
python create_admin.py
```

После этого можно зайти на <http://127.0.0.1:8000/admin> с дефолтными кредами:

| email             | password |
|-------------------|----------|
| `admin@admin.com` | `admin`  |

> Сейчас в админку залогинится любой зарегистрированный юзер (`get_current_admin_user` ещё не проверяет роль — соответствующая ветка закомментирована в `app/users/dependencies.py`).

## Тесты

Стек — `pytest` + `pytest-asyncio` (`asyncio_mode=auto`) + `httpx.AsyncClient` поверх `ASGITransport` (in-process, без поднятия сервера).

Тесты ходят в отдельную БД из `TEST_DB_*` (см. `.env`). Переключение делает `app/conftest.py` — он выставляет `MODE=TEST` до первого импорта `app.config`, а `app/database.py` под этим режимом берёт `TEST_DATABASE_URL` и `NullPool` (чтобы пул соединений не оставался между прогонами).

Сидовые данные лежат в `app/tests/mock_*.json` и заливаются session-scope autouse-фикстурой `prepare_database` (`drop_all` → `create_all` → `INSERT`). После bulk-insert вручную сдвигаются Postgres `SERIAL`-последовательности (`setval(pg_get_serial_sequence(...))`) — иначе следующий `INSERT` из API упирается в дубликат `id=1`.

Особенности фикстур (`app/tests/conftest.py`):

- `ac` — анонимный `AsyncClient`.
- `authenticated_ac` — логинится `test@test.com` / `test` и работает с `access_token` в cookie.
- `session` — открывает `async_session_maker` напрямую для DAO-тестов.
- `_disable_celery_tasks` (autouse) — monkey-patch `send_booking_confirmation_email.delay → no-op`, чтобы тесты не дёргали Redis-брокер и SMTP.

Подготовка тестовой БД (один раз):

```bash
createdb -U postgres test_booking_db
```

Запуск:

```bash
pytest                                            # все тесты
pytest app/tests/unit_tests                       # только unit
pytest app/tests/integration_tests/test_bookings  # подкаталог
pytest -k booking -vv                             # по имени
```

Покрытие:

- `unit_tests/test_users/test_dao.py` — `UsersDao.find_by_id` на сидовых юзерах + отсутствующем id.
- `integration_tests/test_bookings/test_dao.py` — `BookingDAO.add` + `find_by_id`.
- `integration_tests/test_bookings/test_api.py` — параметризированный `POST /v1/bookings` (8 успешных + 9-й 409 по исчерпанию `quantity`) с проверкой `GET /v1/bookings`.
- `integration_tests/test_users/test_api.py` — регистрация (201/409/422) и логин (200/401).

## Статика и шаблоны

- `app/static` смонтирован как `/static` (`StaticFiles`).
- `app/templates` — Jinja2-шаблоны. Пример — `templates/hotels.html`, рендерится в `GET /pages/hotels` через `Jinja2Templates`.

## CORS

В `main.py` подключён `CORSMiddleware` для `http://localhost:3000` (на случай отдельного фронта). Разрешены методы `GET/POST/OPTIONS/DELETE/PATCH/PUT` и заголовки для куки/авторизации.

## Версионирование API

API обёрнут в `VersionedFastAPI` из `fastapi-versioning` (`app/main.py`). Базовое приложение собирает все роутеры, после чего оборачивается в версионированное:

- Эндпоинты без явного `@version(...)` попадают в **`default_version=(1, 0)`**, поэтому весь текущий API доступен под префиксом **`/v1`**.
- **`/latest`** — алиас на самую свежую версию.
- У каждой версии своя изолированная документация: **`/v1/docs`** и схема **`/v1/openapi.json`**. Корневой `/docs` показывает ссылки на версии.
- `lifespan`, `CORSMiddleware`, замер времени запроса, `/static` и админка sqladmin навешиваются на **родительское** приложение уже после сборки — версионер копирует только `APIRoute`, поэтому `Mount`-объекты (static, admin) и middleware нужно подключать к результату.

Добавить новую версию эндпоинта:

```python
from fastapi_versioning import version

@router.get("/me")
@version(2, 0)          # уедет под /v2/auth/me и в /latest
async def read_users_me_v2(...): ...
```

Эндпоинты без `@version` остаются в `/v1`; помеченные `@version(2, 0)` автоматически появляются под `/v2`.

### Эндпоинты

Все пути в таблице ниже доступны под префиксом **`/v1`** (и алиасом `/latest`), например `POST /v1/auth/login`. Без версии остаются служебные маршруты: `/admin`, `/static`, корневой `/docs`, `/redoc`.

| Метод  | Путь                          | Авториз. | Описание                                                                |
|--------|-------------------------------|----------|-------------------------------------------------------------------------|
| POST   | `/auth/register`              | —        | Регистрация — 201 / 409 если email занят                                |
| POST   | `/auth/login`                 | —        | Логин — выдаёт JWT в cookie                                             |
| POST   | `/auth/logout`                | —        | Сброс cookie                                                            |
| GET    | `/auth/me`                    | ✓        | Текущий пользователь                                                    |
| GET    | `/auth/all`                   | админ    | Все пользователи                                                        |
| GET    | `/hotels/{location}`          | —        | Отели в локации с ≥1 свободным номером в период `date_from..date_to`    |
| GET    | `/hotels/id/{hotel_id}`       | —        | Конкретный отель по id                                                  |
| GET    | `/hotels/{hotel_id}/rooms`    | —        | Номера отеля с `total_cost` и `rooms_left` за период                    |
| GET    | `/bookings`                   | ✓        | Бронирования пользователя (с данными номера)                            |
| POST   | `/bookings`                   | ✓        | Создать бронь — 409 если номер занят                                    |
| DELETE | `/bookings/{booking_id}`      | ✓        | Удалить бронь — 204                                                     |
| POST   | `/images/hotels?name={id}`    | —        | Загрузить картинку отеля, кладёт оригинал в `app/static/images` и ставит celery-таск ресайза (1000×500 и 200×100) |
| GET    | `/pages/hotels`               | —        | HTML-страница со списком отелей (Jinja, переиспользует `get_hotels_by_location`) |
| GET    | `/admin`                      | —        | Админ-панель SQLAdmin (Users, Bookings) — **без префикса `/v1`**          |

### Быстрая проверка через curl

```bash
# регистрация
curl -i -X POST http://127.0.0.1:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"12345"}'

# логин (-c сохранит cookie)
curl -i -X POST http://127.0.0.1:8000/v1/auth/login \
  -c cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"12345"}'

# защищённый эндпоинт (-b пошлёт cookie)
curl -i http://127.0.0.1:8000/v1/bookings -b cookies.txt
```
