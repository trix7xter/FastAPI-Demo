from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.hotels.router import get_hotels_by_location

router = APIRouter(prefix="/pages", tags=["Frontend"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/hotels", response_class=HTMLResponse)
async def get_hotels_page(
    request: Request,
    hotels=Depends(get_hotels_by_location),
):
    return templates.TemplateResponse(
        request=request,
        name="hotels.html",
        context={"hotels": hotels},
    )
