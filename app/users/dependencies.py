from datetime import datetime, timezone

from fastapi import Depends, Request
from jose import jwt, JWTError

from app.config import settings
from app.exceptions import (
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotPresentException,
)
from app.users.dao import UsersDao
from app.users.models import Users


def get_token(request: Request) -> str:
    token = request.cookies.get("booking_access_token")
    if not token:
        raise TokenAbsentException
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        raise IncorrectTokenFormatException

    expire = payload.get("exp")
    if not expire or expire < datetime.now(timezone.utc).timestamp():
        raise TokenExpiredException

    user_id = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException

    user = await UsersDao.find_by_id(int(user_id))
    if not user:
        raise UserIsNotPresentException

    return user


async def get_current_admin_user(current_user: Users = Depends(get_current_user)):
    # if current_user.role != "admin":
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return current_user
