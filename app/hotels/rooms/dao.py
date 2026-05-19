from datetime import date

from sqlalchemy import and_, func, select

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms


class RoomDAO(BaseDAO):
    model = Rooms

    @classmethod
    async def find_all(
        cls,
        hotel_id: int,
        date_from: date,
        date_to: date,
    ):
        async with async_session_maker() as session:
            booked_rooms = (
                select(Bookings.room_id, func.count().label("cnt"))
                .where(
                    and_(
                        Bookings.date_from < date_to,
                        Bookings.date_to > date_from,
                    )
                )
                .group_by(Bookings.room_id)
                .cte("booked_rooms")
            )

            days = (date_to - date_from).days

            rooms_left = Rooms.quantity - func.coalesce(booked_rooms.c.cnt, 0)

            query = (
                select(
                    Rooms.__table__.columns,
                    (Rooms.price * days).label("total_cost"),
                    rooms_left.label("rooms_left"),
                )
                .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                .where(Rooms.hotel_id == hotel_id)
            )

            result = await session.execute(query)
            return result.mappings().all()
