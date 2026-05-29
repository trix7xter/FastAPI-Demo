import json
from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert, text

from app.bookings.models import Bookings
from app.config import settings
from app.database import Base, async_session_maker, engine
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.main import app as fastapi_app
from app.users.models import Users


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", "r", encoding="utf-8") as file:
            return json.load(file)

    hotels = open_mock_json("hotels")
    rooms = open_mock_json("rooms")
    users = open_mock_json("users")
    bookings = open_mock_json("bookings")

    for booking in bookings:
        booking["date_from"] = datetime.strptime(
            booking["date_from"], "%Y-%m-%d"
        ).date()
        booking["date_to"] = datetime.strptime(booking["date_to"], "%Y-%m-%d").date()

    async with async_session_maker() as session:
        add_hotels = insert(Hotels).values(hotels)
        add_rooms = insert(Rooms).values(rooms)
        add_users = insert(Users).values(users)
        add_bookings = insert(Bookings).values(bookings)

        await session.execute(add_hotels)
        await session.execute(add_rooms)
        await session.execute(add_users)
        await session.execute(add_bookings)

        # Realign Postgres SERIAL sequences with the explicit IDs we just
        # bulk-inserted; otherwise the next API insert reuses id=1 and trips
        # the primary-key unique constraint.
        for table in ("hotels", "rooms", "users", "bookings"):
            await session.execute(
                text(
                    f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                    f"COALESCE((SELECT MAX(id) FROM {table}), 1))"
                )
            )

        await session.commit()


@pytest.fixture(autouse=True)
def _disable_celery_tasks(monkeypatch):
    # Celery broker (Redis) and SMTP are not available during tests,
    # so any .delay() call would block or fail. Replace with no-op.
    from app.tasks import tasks as task_module

    monkeypatch.setattr(
        task_module.send_booking_confirmation_email,
        "delay",
        lambda *args, **kwargs: None,
    )


@pytest.fixture(scope="function")
async def ac():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test.com") as ac:
        yield ac


@pytest.fixture(scope="function")
async def authenticated_ac():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test.com") as ac:
        await ac.post(
            "/v1/auth/login", json={"email": "test@test.com", "password": "test"}
        )
        assert ac.cookies["access_token"]
        yield ac


@pytest.fixture(scope="function")
async def session():
    async with async_session_maker() as session:
        yield session
