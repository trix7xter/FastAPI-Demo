from datetime import date
from typing import Optional

from fastapi import FastAPI, Query, Depends
from pydantic import BaseModel
from app.booking.router import router as router_bookings
from app.users.router import router as router_users

app = FastAPI()

app.include_router(router_users)
app.include_router(router_bookings)


class HotelsSearchArgs:
    def __init__(
        self,
        location,
        date_from: date,
        date_to: date,
        stars: Optional[int] = Query(None, ge=1, le=5),
        has_spa: Optional[bool] = None,
    ):
        self.location = location
        self.date_from = date_from
        self.date_to = date_to
        self.stars = stars
        self.has_spa = has_spa


class SHotel(BaseModel):
    address: str
    name: str
    stars: int
    has_spa: bool


@app.get("/hotels")
def get_hotels(search_args: HotelsSearchArgs = Depends()) -> list[SHotel]:
    hotels = [
        SHotel(
            address="Gagarina Street, 1, Altay",
            name="Super Hotel",
            stars=5,
            has_spa=True,
        )
    ]
    return hotels


class SBooking(BaseModel):
    room_id: int
    date_from: date
    date_to: date


@app.post("/booking")
def add_booking(booking: SBooking):
    pass
