from fastapi import FastAPI

from app.bookings.router import router as router_bookings
from app.hotels.router import router as router_hotels
from app.users.router import router as router_users

import app.hotels.rooms.router  # noqa: F401  attaches /hotels/{hotel_id}/rooms endpoint

app = FastAPI()

app.include_router(router_users)
app.include_router(router_hotels)
app.include_router(router_bookings)
