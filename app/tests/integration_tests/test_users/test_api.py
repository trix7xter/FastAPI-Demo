from httpx import AsyncClient
import pytest


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("testemail@mail.ru", "testpassword", 201),
        ("test@test.com", "test", 409),
        ("failemail", "testpassword", 422),
    ],
)
async def test_register_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post(
        "/auth/register", json={"email": email, "password": password}
    )

    assert response.status_code == status_code


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("artem@example.com", "test", 200),
        ("test@test.com", "test", 200),
        ("artem@example.com", "wrong", 401),
    ],
)
async def test_login_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post(
        "/auth/login", json={"email": email, "password": password}
    )

    assert response.status_code == status_code
