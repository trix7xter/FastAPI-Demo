import asyncio
from datetime import date

from fastapi import APIRouter

from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotel, SHotelInfo
from fastapi_cache.decorator import cache

router = APIRouter(prefix="/hotels", tags=["Hotels & Rooms"])


@router.get("/{location}", response_model=list[SHotelInfo])
@cache(expire=30)
async def get_hotels_by_location(
    location: str,
    date_from: date,
    date_to: date,
):
    return HotelDAO.find_all(location, date_from, date_to)


@router.get("/id/{hotel_id}", response_model=SHotel | None)
async def get_hotel_by_id(hotel_id: int):
    return await HotelDAO.find_by_id(hotel_id)
