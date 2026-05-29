from datetime import date

from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.schemas import SRoomInfo
from app.hotels.router import router


@router.get("/{hotel_id}/rooms", response_model=list[SRoomInfo])
async def get_rooms_by_hotel(
    hotel_id: int,
    date_from: date,
    date_to: date,
):
    return await RoomDAO.find_all(hotel_id, date_from, date_to)
