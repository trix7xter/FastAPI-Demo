from datetime import date

from sqlalchemy import and_, func, select

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_all(
        cls,
        location: str,
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

            booked_hotels = (
                select(
                    Rooms.hotel_id.label("hotel_id"),
                    func.sum(func.coalesce(booked_rooms.c.cnt, 0)).label(
                        "rooms_booked"
                    ),
                )
                .select_from(Rooms)
                .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                .group_by(Rooms.hotel_id)
                .cte("booked_hotels")
            )

            rooms_left = Hotels.rooms_quantity - func.coalesce(
                booked_hotels.c.rooms_booked, 0
            )

            query = (
                select(  # pyright: ignore[reportCallIssue]
                    Hotels.__table__.columns,  # pyright: ignore[reportArgumentType]
                    rooms_left.label("rooms_left"),
                )
                .join(
                    booked_hotels,
                    booked_hotels.c.hotel_id == Hotels.id,
                    isouter=True,
                )
                .where(
                    and_(
                        Hotels.location.ilike(f"%{location}%"),
                        rooms_left >= 1,
                    )
                )
            )

            result = await session.execute(query)
            return result.mappings().all()
