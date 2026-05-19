from pydantic import BaseModel, ConfigDict


class SHotel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: str
    services: list[str] | None
    rooms_quantity: int
    image_id: int | None


class SHotelInfo(SHotel):
    rooms_left: int
