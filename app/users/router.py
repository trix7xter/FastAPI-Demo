from fastapi import APIRouter, Depends, Response, status

from app.exceptions import IncorrectEmailOrPasswordException, UserAlreadyExistsException
from app.users.auth import authenticate_user, create_access_token, get_password_hash
from app.users.dao import UsersDao
from app.users.dependencies import get_current_admin_user, get_current_user
from app.users.models import Users
from app.users.schemas import SUserAuth

router = APIRouter(
    prefix="/auth",
    tags=["Auth and Users"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: SUserAuth):
    existing_user = await UsersDao.find_one_or_none(email=user_data.email)
    if existing_user:
        raise UserAlreadyExistsException
    hashed_password = get_password_hash(user_data.password)
    await UsersDao.add(email=user_data.email, hashed_password=hashed_password)
    return {"email": user_data.email}


@router.post("/login")
async def login_user(response: Response, user_data: SUserAuth):
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("access_token", access_token, httponly=True)
    return {"access_token": access_token}


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("access_token")


@router.get("/me")
async def read_users_me(current_user: Users = Depends(get_current_user)):
    return current_user


@router.get("/all")
async def read_users_all(_: Users = Depends(get_current_admin_user)):
    return await UsersDao.find_all()
