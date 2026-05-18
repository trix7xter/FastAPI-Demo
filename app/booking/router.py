from fastapi import APIRouter, Depends
from sqlalchemy import select
from app.booking.dao import BookingDAO
from app.booking.models import Bookings
from app.database import async_session_maker
from app.booking.schemas import SBooking
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("", response_model=list[SBooking])
async def get_bookings(user: Users = Depends(get_current_user)):
    return await BookingDAO.find_all()


async def get_bookings_by_user_id(user: Users = Depends(get_current_user)):
    return await BookingDAO.find_all(user_id=user.id)
