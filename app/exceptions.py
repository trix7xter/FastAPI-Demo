from fastapi import HTTPException, status


class Exception(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(Exception):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"


class IncorrectEmailOrPasswordException(Exception):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверная почта или пароль"


class TokenExpiredException(Exception):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истёк"


class TokenAbsentException(Exception):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен отсутствует"


class IncorrectTokenFormatException(Exception):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Некорректный формат токена"


class UserIsNotPresentException(Exception):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Пользователь не найден"


class RoomCannotBeBooked(Exception):
    status_code = status.HTTP_409_CONFLICT
    detail = "Комната не может быть забронирована"
