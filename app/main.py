import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_versioning import VersionedFastAPI
from redis import asyncio as aioredis
from sqladmin import Admin

from app.admin.auth import authentication_backend
from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UserAdmin
from app.bookings.router import router as router_bookings
from app.config import settings
from app.database import engine

# Side-effect import: registers /hotels/{hotel_id}/rooms endpoint on router_hotels
from app.hotels.rooms import router as _rooms_router  # noqa: F401
from app.hotels.router import router as router_hotels
from app.images.router import router as router_images
from app.pages.router import router as router_pages
from app.users.router import router as router_users
from app.logger import logger


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    await redis.close()


# Base app only collects the routers. Each endpoint may carry a `@version(...)`
# marker; endpoints without one fall back to `default_version` below.
base_app = FastAPI()

base_app.include_router(router_users)
base_app.include_router(router_hotels)
base_app.include_router(router_bookings)
base_app.include_router(router_pages)
base_app.include_router(router_images)

# Wrap the base app into a versioned one. The whole current API has no explicit
# `@version` markers, so it lands under `/v1` (default_version=(1, 0)).
# `/latest` always aliases the highest available version. Each version also gets
# its own isolated docs at `/v{n}/docs` and schema at `/v{n}/openapi.json`.
# lifespan is forwarded to the parent app so the Redis cache is initialised once.
app = VersionedFastAPI(
    base_app,
    version_format="{major}",
    prefix_format="/v{major}",
    default_version=(1, 0),
    enable_latest=True,
    lifespan=lifespan,
)

# Mounts and middleware must be attached to the parent app *after* building it:
# VersionedFastAPI only copies APIRoutes into the versioned sub-apps and would
# choke on Mount objects, and middleware on `base_app` would never run.
app.mount("/static", StaticFiles(directory="app/static"), "static")

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info("Request handing time", extra={"process_time": round(process_time, 4)})
    return response


admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UserAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)
