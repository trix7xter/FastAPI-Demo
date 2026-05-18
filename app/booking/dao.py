from sqlalchemy import select

from app.booking.models import Bookings
from app.dao.base import BaseDAO


class BookingDAO(BaseDAO):
    model = Bookings
