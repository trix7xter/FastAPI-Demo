from datetime import date

from sqlalchemy import and_, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms
from app.logger import logger


class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def find_all(cls, user_id: int):
        try:
            async with async_session_maker() as session:
                query = (
                    select(
                        Bookings.room_id,
                        Bookings.user_id,
                        Bookings.date_from,
                        Bookings.date_to,
                        Bookings.price,
                        Bookings.total_cost,
                        Bookings.total_days,
                        Rooms.image_id,
                        Rooms.name,
                        Rooms.description,
                        Rooms.services,
                    )
                    .join(Rooms, Rooms.id == Bookings.room_id)
                    .where(Bookings.user_id == user_id)
                )
                result = await session.execute(query)
                return result.mappings().all()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            else:
                msg = "Unknown Exc"
            msg += ": Cannot find bookings"
            logger.error(msg, extra={"user_id": user_id}, exc_info=True)
            return None

    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ) -> Bookings | None:
        try:
            async with async_session_maker() as session:
                booked_rooms = (
                    select(Bookings)
                    .where(
                        and_(
                            Bookings.room_id == room_id,
                            or_(
                                and_(
                                    Bookings.date_from >= date_from,
                                    Bookings.date_from <= date_to,
                                ),
                                and_(
                                    Bookings.date_from <= date_from,
                                    Bookings.date_to > date_from,
                                ),
                            ),
                        )
                    )
                    .cte("booked_rooms")
                )

                rooms_left = (
                    select(
                        (Rooms.quantity - func.count(booked_rooms.c.room_id)).label(
                            "rooms_left"
                        )
                    )
                    .select_from(Rooms)
                    .join(
                        booked_rooms,
                        booked_rooms.c.room_id == Rooms.id,
                        isouter=True,
                    )
                    .where(Rooms.id == room_id)
                    .group_by(Rooms.quantity, booked_rooms.c.room_id)
                )

                rooms_left_result = await session.execute(rooms_left)
                rooms_left_value = rooms_left_result.scalar()

                if rooms_left_value and rooms_left_value > 0:
                    price_query = select(Rooms.price).where(Rooms.id == room_id)
                    price_result = await session.execute(price_query)
                    price = price_result.scalar()

                    add_booking = (
                        insert(Bookings)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        .returning(Bookings)
                    )
                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.scalar()
                return None
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            else:
                msg = "Unknown Exc"
            msg += ": Cannot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            logger.error(msg, extra=extra, exc_info=True)
            return None
