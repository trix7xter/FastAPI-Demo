"""One-off script to create an admin user for the SQLAdmin panel.

Usage:
    python create_admin.py
"""
import asyncio

from sqlalchemy import select

from app.database import async_session_maker
from app.users.auth import get_password_hash
from app.users.models import Users
# Import all models so SQLAlchemy can resolve cross-module relationships
from app.bookings.models import Bookings  # noqa: F401
from app.hotels.models import Hotels  # noqa: F401
from app.hotels.rooms.models import Rooms  # noqa: F401

ADMIN_EMAIL = "admin@admin.com"
ADMIN_PASSWORD = "admin"


async def create_admin() -> None:
    async with async_session_maker() as session:
        existing = await session.execute(
            select(Users).where(Users.email == ADMIN_EMAIL)
        )
        if existing.scalar_one_or_none():
            print(f"Admin user {ADMIN_EMAIL} already exists")
            return

        user = Users(
            email=ADMIN_EMAIL,
            hashed_password=get_password_hash(ADMIN_PASSWORD),
        )
        session.add(user)
        await session.commit()
        print(f"Created admin user: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(create_admin())
